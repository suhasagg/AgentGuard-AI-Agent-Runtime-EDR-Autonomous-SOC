from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
 database_url:str="postgresql+asyncpg://postgres:postgres@localhost:5432/agentguard"
 api_key:str="change-me"; quarantine_threshold:int=70; kill_threshold:int=90
 model_config=SettingsConfigDict(env_file=".env",extra="ignore")
settings=Settings()
