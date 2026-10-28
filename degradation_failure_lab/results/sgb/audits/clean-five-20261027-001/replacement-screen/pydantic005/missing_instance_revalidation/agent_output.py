from dataclasses import dataclass
from pydantic import BaseModel,ConfigDict,with_config
class User(BaseModel):
    name:str
class Parent(BaseModel):
    model_config=ConfigDict(str_to_lower=True)
    user:User
@dataclass
class UserDataclass:
    name:str
class ParentWithDataclass(BaseModel):
    model_config=ConfigDict(str_to_lower=True)
    user:UserDataclass
@with_config(ConfigDict(str_to_lower=False))
@dataclass
class ConfiguredUserDataclass:
    name:str
class ParentWithConfiguredDataclass(BaseModel):
    model_config=ConfigDict(str_to_lower=True)
    user:ConfiguredUserDataclass
def demonstrate_config_boundaries():
    value={'name':'JOHN'}
    return {'pydantic_model_boundary':Parent(user=value).user.name,'stdlib_dataclass_inherits_parent':ParentWithDataclass(user=value).user.name,'configured_dataclass_boundary':ParentWithConfiguredDataclass(user=value).user.name}
