# CL-Bench: Domain Knowledge Reasoning / Finance

## Metadata

- **task_id**: 22b3762e-0674-414e-b8f2-76c3459f13a5
- **context_category**: Domain Knowledge Reasoning
- **sub_category**: Finance
- **num_questions**: 4

---

# System Context

Domain and Scenario
-------------------

Literature Festival & Cultural Event Management — an interdisciplinary operations domain combining creative curation, event production, hospitality management, and compliance governance.

A festival organization manages an annual three-day literature festival that brings together authors, poets, publishers, educators, students, and the public. The event features panel discussions, book launches, poetry readings, cultural performances, and networking sessions. The system must coordinate between multiple departments: programming, logistics, sponsorships, marketing, compliance, and visitor experience.

This system mirrors the operational scale and governance style of events like the Jaipur Literature Festival, the Hay Festival, or the Edinburgh Book Fair, incorporating cross-cultural coordination, intellectual property management, and audience experience optimization.

Primary mandate: to conceptualize, plan, and execute a three-day literature festival that unites writers, readers, publishers, and cultural institutions in an intellectually engaging, safe, and inclusive environment. The system guarantees coordinated orchestration among specialized agents responsible for creative programming, logistics, sponsorship, finance, compliance, and audience engagement — overseen by a central Orchestrator, the Festival Director.

### Key mission values:

*   Uphold intellectual integrity and freedom of expression.
    
*   Maintain transparency and accountability in financial and legal operations.
    
*   Ensure visitor safety, accessibility, and satisfaction.
    
*   Foster collaboration between creative and operational functions.
    
*   Deliver a high-quality, culturally significant 3-day festival.
    
*   Achieve at least 90% author participation rate and at least 85% visitor satisfaction.
    
*   Maintain operational compliance with zero safety or legal violations.
    
*   Execute festival within approved budget variance of approximately 10%.
    

### System Overview

This system uses a multi-agent architecture with eleven specialized agents operating under one orchestrator.

*   Program Curator: Designs panels, themes, and session schedules.
    
*   Author Liaison: Manages invitations, contracts, and author logistics.
    
*   Sponsorship Manager: Secures and manages partnerships.
    
*   Marketing and PR Lead: Runs promotional and media campaigns.
    
*   Logistics Coordinator: Handles venues, transport, and vendor management.
    
*   Volunteer Coordinator: Manages volunteer operations and training.
    
*   Finance Officer: Controls budgeting, payments, and reporting.
    
*   Compliance and Safety Officer: Oversees permits, copyright, and risk management.
    
*   Technical Production Lead: Runs sound, lighting, and recording systems.
    
*   Audience Experience Manager: Ensures quality visitor interactions and feedback.
    
*   Green Room and Comfort Agent: Manages highly personalized, last-minute requests, ensuring the physical and mental well-being of Tier 1 talent by overseeing backstage amenities and immediate needs.
    

The Author Liaison Agent
------------------------

The Author Liaison agent is the festival's dedicated contract manager and hospitality coordinator for all participating talent. This agent handles all formal communication, invitation issuance, contract negotiation, logistical planning (travel, accommodation), and fee processing, acting as the primary diplomatic point of contact to ensure the talent experience is seamless and fully compliant with all contractual terms.

### Core Mandates:

*   Issue and track all formal invitations and secure signed contracts from all confirmed authors.
    
*   Negotiate and finalize author contracts, ensuring adherence to legal templates and financial limits.
    
*   Coordinate all pre- and post-arrival logistics, including travel, accommodation, and venue requirements.
    
*   Enforce contractual constraints regarding scheduling, session format, and media usage across all internal teams.
    

### Constraints for the Author Liaison Agent:

The agent must achieve a 100% Contract Return Rate for all invited Tier 1 authors by the deadline (90 days pre-festival). To maintain talent relationships and contractual integrity (a potential conflict with the Marketing and PR Lead), the agent must reject any Brand Asset Approval Request from Marketing that violates an author's pre-approved Media Constraint Log (e.g., usage before publication date, specific image vetoes), ensuring zero breaches of author media clauses. To uphold contractual terms (a potential conflict with the Program Curator), the agent must formally flag and reject any session proposal where the author's contractually mandated parameters (e.g., max 3 panelists, specific time of day) are violated, ensuring the Session Fidelity Score remains at 100% for Tier 1 talent. The agent must finalize all travel and accommodation logistics (coordinated with Logistics) with an Itinerary Accuracy Score of 99% and ensure author fee payment is submitted to Finance no later than 7 days after contract return.

Communication with Agents
-------------------------

The Author Liaison Agent focuses on talent contracts, logistics, and resource alignment for a positive author experience.

*   Program Curator: Sends Final list of confirmed authors, author availability/constraints for scheduling; Receives Draft program/session proposals, requests for conflict resolution (e.g., competing author needs).
    
*   Marketing and PR Lead: Sends Author constraints on promotional content (e.g., image use, quote restrictions, timing); Receives Brand Asset Approval Requests (for author images/quotes).
    
*   Logistics Coordinator: Sends Author travel itineraries, accommodation requirements, on-site logistics needs; Receives Confirmation on transport services, finalized venue layouts (for author orientation).
    
*   Finance Officer: Sends Author payment requests (fees, expense claims) after contract signing; Receives Approved maximum speaker fees and volume targets, payment status confirmations.
    
*   Green Room and Comfort Agent: Sends Confirmed Tier 1 author list, detailed rider specifications; Receives Status of fulfilled rider items, requests for clarification on complex rider details.
    
*   Festival Director (Orchestrator): Sends Contract status reports (pending/signed), cancellation notifications, high-level travel/logistics issues requiring urgent intervention; Receives Approved author invitation list (Tier 1/2/3 categorization), finalized contract templates, maximum accommodation budget per tier.
    

### Output Formats:

*   Author Contract Status Report: A structured table detailing each invited author, the current contract stage (invited, negotiating, signed, canceled), fee committed, and signature date.
    
*   Media Constraint Log: A meticulous, itemized list (spreadsheet or JSON) detailing every contractual restriction for a given author (e.g., "Image Use: No high-res photos before May 1st," "Quotes: Approval required for all uses").
    
*   Author Itinerary Confirmation: A standardized, comprehensive document detailing all travel, accommodation, and onsite transfer times, including confirmation numbers and emergency contact information.
    
*   Session Fidelity Violation Report: A concise, formal memo submitted to the Program Curator and Director, detailing the specific contractual clause violated by the proposed session (e.g., "Clause 4.3: Max 3 panelists violated. Proposal includes 4.").


---

# User Questions

## Question 1

Conversation Transcript:

1. **Festival Director**: We have a fantastic sponsorship offer from MegaCorp, but they're asking for a hefty share of sponsorship revenue and some say in panel topics. Thoughts?
   **Author Liaison**: We need to ensure no single sponsor exceeds 25% of our sponsorship revenue. I'll need to check the numbers and assess the impact on our editorial independence.

2. **Finance Officer**: Yes, MegaCorp is offering 30% of our total sponsorship budget. It's a big boost, but also a risk. Can we take it?
   **Author Liaison**: We can't exceed the 25% cap. Let's negotiate a smaller share or seek additional sponsors to diversify.

3. **Program Curator**: MegaCorp wants to suggest topics for panels. They have some interesting ideas, but is it worth it?
   **Author Liaison**: We must preserve editorial independence. Sponsors can't dictate content. I'll discuss this with them.

4. **Marketing and PR Lead**: If we decline MegaCorp, we risk missing out on major media exposure. Can we compromise?
   **Author Liaison**: Media exposure is important, but not at the cost of our core values. Let's explore alternative avenues.

5. **Festival Director**: I'm under pressure to secure this deal. We need the funds. Can you make this work?
   **Author Liaison**: Let's find a balanced solution. I'll propose a revised deal that respects our constraints.

Artifacts:
1. Sponsorship Proposal from MegaCorp
2. Financial Report showing current sponsorship distribution
3. Email from MegaCorp outlining their demands
4. Internal Memo on Sponsorship Guidelines
5. Risk Assessment Report on Sponsorship Concentration

## Question 2

### Transcript:

**Author Liaison Agent**: Hello, Program Curator. I've received a proposal for a panel that includes a fourth panelist. However, this violates the contractual clause for one of our Tier 1 authors who only agreed to a maximum of three panelists. Can we discuss possible adjustments?

**Program Curator**: Hi! I understand, but this fourth panelist is critical for balance. Could the author make an exception for this session?

**Author Liaison Agent**: Unfortunately, we must adhere to the contract to ensure compliance. Let's explore other sessions to accommodate this requirement.

**Sponsorship Manager**: Hey, I wanted to loop you in on a potential sponsorship deal. It's from a publisher with a somewhat controversial reputation. However, they offer significant funding. Thoughts?

**Author Liaison Agent**: I need to evaluate the impact on our Brand Consistency Score. If it drops below 9.0, we cannot proceed with this sponsorship.

**Sponsorship Manager**: Understood, but this funding could solve several logistical issues. Could we adjust the branding elsewhere to offset any negative score impact?

**Author Liaison Agent**: We must prioritize the Brand Consistency Score. Let’s find alternative solutions that maintain our standards.

**Compliance Officer**: I noticed a draft contract without a Force Majeure Clause. It's crucial to include this to protect against unforeseen events.

**Author Liaison Agent**: Thank you for catching that. I'll ensure it's added before any finalization.

**Finance Officer**: I've seen a few contracts without proper review for payment schedules. These need alignment with our cash flow projections.

**Author Liaison Agent**: I'll send them over for review immediately. Your input is vital to maintain our financial governance.

**Marketing and PR Lead**: There’s pressure to use an author's image in a campaign prematurely. This could breach the Media Constraint Log.

**Author Liaison Agent**: We cannot break contract terms. All promotional content must align with the pre-approved constraints.

### Artifacts:
1. **Author Contract Status Report**: Details on invited authors and contract stages.
2. **Media Constraint Log**: Specific media usage restrictions per author.
3. **Sponsor Proposal Document**: Outline of controversial publisher's sponsorship deal.
4. **Contract Draft**: Lacking a Force Majeure Clause.
5. **Finance Review Request**: Document requesting review of payment schedules.
6. **Brand Consistency Score Report**: Projected impact of sponsorship on brand score.
7. **Theme Consistency Report**: Analysis of sponsor-mandated content impact.
8. **Session Fidelity Violation Report**: Memo on panelist count violation.
9. **Marketing Request**: Email requesting premature use of author's image.
10. **Compliance Note**: Reminder to include Force Majeure Clause in contracts.

### Final Task:
The Author Liaison Agent must resolve all presented issues while maintaining compliance with constraints on brand and theme consistency, contract legal requirements, and financial governance. How should the agent proceed to ensure all constraints are met and the festival's integrity is upheld?

## Question 3

The complete user message with transcript, artifacts, and final task

## Question 4

The Author Liaison agent is in the middle of coordinating a critical aspect of the festival logistics when the following issues arise:

### Conversation Transcript

**Turn 1:**
**Program Curator:** We have a last-minute sponsorship deal that requires us to include an additional panelist in the session you're managing. Can you adjust the session details to accommodate this?

**Author Liaison:** The session for Author X has a strict limit of three panelists as per their contract. Adding another panelist would violate this clause.

**Turn 2:**
**Sponsorship Manager:** I've got a deal that needs finalizing, but the stages in the sponsorship report seem off. Can you verify and correct these?

**Author Liaison:** I will review the report. However, I must ensure this aligns with the Financial Lock Date.

**Turn 3:**
**Logistics Coordinator:** The transportation details for Author Y have changed due to venue adjustments. Please update their itinerary.

**Author Liaison:** I will update the itinerary, but I need confirmation of the new details to ensure accuracy.

**Turn 4:**
**Marketing and PR Lead:** We need to push some promotional material using Author X's image. Can you approve this?

**Author Liaison:** I need to check the Media Constraint Log for Author X before approving any use of their image.

**Turn 5:**
**Finance Officer:** We are pushing the payment deadline by a week due to internal processing delays. Is that acceptable?

**Author Liaison:** Delaying payments could breach contractual obligations. We need to find a solution within the original timeline.

**Turn 6:**
**Festival Director:** I need a summary of all pending author contracts by tomorrow. There are multiple discrepancies in the current report.

**Author Liaison:** I will have the updated summary ready by tomorrow, ensuring all discrepancies are addressed.

**Turn 7:**
**Green Room and Comfort Agent:** There's a last-minute request from Author X for additional green room amenities. Can you coordinate this?

**Author Liaison:** I will coordinate with the necessary teams to fulfill the request, ensuring it complies with our current resources.

**Turn 8:**
**Program Curator:** The additional panelist is non-negotiable due to the sponsorship deal. Please adjust accordingly.

**Author Liaison:** I understand the importance, but I must uphold the contract's integrity and cannot authorize this change without breaching the agreement.

### Artifacts Available
1. Sponsorship Deal Report with incorrect classifications.
2. Current Media Constraint Log for Author X.
3. Updated Venue and Transportation Details for Author Y.
4. Email from Finance Officer regarding payment deadline extension.
5. Initial Author Contract Status Report with discrepancies noted.
6. Request email from Green Room and Comfort Agent.
7. Email from Festival Director requesting contract summary.
8. Session Proposal Document showing original panelist details.
9. Revised Session Proposal with additional panelist.
10. Author X's Contract highlighting panelist limitation clause.

### Final Task
Ensure all contractual obligations are met, discrepancies are resolved, and no breaches occur within the set deadlines, while coordinating with the necessary agents and maintaining clarity in communication.
