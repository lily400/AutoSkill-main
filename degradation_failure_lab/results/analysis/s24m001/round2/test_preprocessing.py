import unittest

from AutoSkill4Doc.document import windowing as w
from AutoSkill4Doc.ingest import _looks_like_front_matter_heading
from AutoSkill4Doc.models import DocumentRecord, DocumentSection, TextSpan
from fidelity import assert_rule_fidelity


class PreprocessingFixTest(unittest.TestCase):
    def test_uri_userinfo_is_not_author_evidence(self):
        for heading, preview in [("FTP", "URI: `ftp://user:pass@host/path`"),
                                 ("SSH", "Connect via ssh://user@host"),
                                 ("API", "Pass `user@example.org` as an argument.")]:
            with self.subTest(heading=heading):
                self.assertFalse(_looks_like_front_matter_heading(heading, preview=preview))

    def test_real_author_contact_and_abstract_are_still_noise(self):
        self.assertTrue(_looks_like_front_matter_heading("Jane Doe", preview="jane@example.org"))
        self.assertTrue(_looks_like_front_matter_heading("Jane Doe1", preview="University"))
        self.assertTrue(_looks_like_front_matter_heading("Author", preview="Email: jane@example.org"))
        self.assertTrue(_looks_like_front_matter_heading("Abstract", preview="Summary of the paper"))

    def test_intro_before_long_parameter_list_is_retained(self):
        text = ("Request options are described below.\n- `timeout`: " + "Wait for completion. " * 25).strip()
        section = DocumentSection(heading="Client", text=text, span=TextSpan(0, len(text)))
        blocks = w._build_paragraph_blocks(section, anchor_markers=[], priority_markers=[])
        self.assertEqual([text], [b.text for b in blocks])

    def test_long_exception_then_indented_list_is_retained(self):
        text = "When the server rejects this operation, leave the existing object unchanged. " * 6
        text += "\n  - `retry`: disabled unless explicitly requested."
        section = DocumentSection(heading="Client", text=text, span=TextSpan(0, len(text)))
        self.assertEqual([text], [b.text for b in w._build_paragraph_blocks(section, anchor_markers=[], priority_markers=[])])

    def test_dialogue_and_long_unstructured_prose_are_still_filtered(self):
        for text in ["Therapist: hello\nClient: hello\nTherapist: welcome", "Narrative description. " * 30]:
            section = DocumentSection(heading="Example", text=text, span=TextSpan(0, len(text)))
            self.assertEqual([], w._build_paragraph_blocks(section, anchor_markers=[], priority_markers=[]))

    def test_window_identity_includes_location_and_content(self):
        record = DocumentRecord(doc_id="fixture", source_type="document", title="API", raw_text="fixture", content_hash="fixture")
        section = DocumentSection(heading="Options", text="fixture")
        def make(text, start):
            return w._window_from_blocks(record=record, section=section,
                blocks=[w.ParagraphBlock(index=2, text=text, span=TextSpan(start, start + len(text)), anchor_hits=())],
                effective_strategy="strict").window_id
        first = make("Default retry is disabled.", 100)
        self.assertEqual(first, make("Default retry is disabled.", 100))
        self.assertNotEqual(first, make("Default retry is disabled.", 500))
        self.assertNotEqual(first, make("Default retry is enabled.", 100))


class ScrapyFidelityTest(unittest.TestCase):
    source = ""
    record = None
    windows = []
    historical_windows = []
    checkpoint_dir = None

    def test_ftp_section_and_duplicate_support_survive(self):
        ftp = next((s for s in self.record.sections if s.heading == "FTP"), None)
        self.assertIsNotNone(ftp)
        self.assertIn("storage backend is: `True`", ftp.text)
        self.assertIn("`overwrite`", ftp.text)

    def test_main_rule_and_exception_share_one_actual_window(self):
        good = []
        for window in self.windows:
            try:
                assert_rule_fidelity(self.source, window.text)
                good.append(window)
            except AssertionError:
                pass
        self.assertGreaterEqual(len(good), 1)

    def test_window_ids_are_unique(self):
        self.assertEqual(len(self.windows), len({window.window_id for window in self.windows}))

    def test_checkpoint_keeps_every_window_and_resume_identity(self):
        from AutoSkill4Doc.store.intermediate import IntermediateRunWriter
        writer = IntermediateRunWriter(base_store_root=str(self.checkpoint_dir), run_id="offline-contract")
        for window in self.windows:
            writer.write_extract_window_progress(record=self.record, window=window, supports=[], drafts=[])
        processed = writer.processed_extract_window_ids(self.record.doc_id)
        self.assertEqual(len(self.windows), len(processed))
        reopened = IntermediateRunWriter(base_store_root=str(self.checkpoint_dir), run_id="offline-contract", resume_existing=True)
        self.assertEqual(set(processed), set(reopened.processed_extract_window_ids(self.record.doc_id)))

    def test_historical_windows_fail_target_fidelity_gate(self):
        for window in self.historical_windows:
            with self.assertRaises(AssertionError):
                assert_rule_fidelity(self.source, window["text"])

    def test_fidelity_gate_rejects_missing_definition_exception_and_wrong_default(self):
        text = "\n".join(self.source.splitlines()[437:449])
        assert_rule_fidelity(self.source, text)
        for changed in [text.replace("`overwrite`", "`item_filter`"),
                        text.replace("- FTP: `True`", "- FTP: `False`"),
                        text.replace("`APPE`", "`OTHER`"),
                        text.split("Some FTP servers")[0]]:
            with self.subTest(changed=changed):
                with self.assertRaises(AssertionError):
                    assert_rule_fidelity(self.source, changed)


class NativeAdmissionTest(unittest.TestCase):
    def test_reference_asset_with_constraints_does_not_require_workflow(self):
        from AutoSkill4Doc.stages.extractor import LLMDocumentSkillExtractor
        from AutoSkill4Doc.taxonomy import load_skill_taxonomy
        extractor = object.__new__(LLMDocumentSkillExtractor)
        extractor.taxonomy = load_skill_taxonomy(domain_type="")
        record = DocumentRecord(doc_id="fixture", source_type="document", title="Fixture", raw_text="A constraint", content_hash="fixture")
        item = {"name": "Storage reference", "description": "A reusable storage constraint.",
                "prompt": "# Rules & Constraints\n- Preserve the documented backend defaults.",
                "asset_type": "knowledge_reference", "granularity": "macro",
                "constraints": ["Preserve the documented backend defaults."]}
        support, draft = extractor._build_support_and_draft(record=record, section_heading="Fixture",
            span=TextSpan(0, 12), unit_text="A constraint", unit_type="window", item=item)
        self.assertIsNotNone(support)
        self.assertIsNotNone(draft)
        self.assertEqual([], draft.workflow_steps)
        self.assertTrue(draft.constraints)

    def test_reference_without_execution_or_constraint_content_is_rejected(self):
        from AutoSkill4Doc.stages.extractor import LLMDocumentSkillExtractor
        extractor = object.__new__(LLMDocumentSkillExtractor)
        item = {"name": "Reference", "description": "Reference material.", "prompt": "Reference material."}
        self.assertEqual((None, None), extractor._build_support_and_draft(record=None, section_heading="Fixture",
            span=TextSpan(0, 12), unit_text="A reference", unit_type="window", item=item))
