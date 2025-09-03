"""
Configuration management for EvolvingTrader
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class TradingConfig(BaseSettings):
    """Trading strategy configuration"""
    initial_capital: float = Field(default=1000.0, env="INITIAL_CAPITAL")
    max_position_size: float = Field(default=0.1, env="MAX_POSITION_SIZE")
    risk_per_trade: float = Field(default=0.02, env="RISK_PER_TRADE")
    max_daily_loss: float = Field(default=0.05, env="MAX_DAILY_LOSS")
    
    # Strategy parameters
    strategy_update_frequency: int = Field(default=3600, env="STRATEGY_UPDATE_FREQUENCY")
    llm_analysis_frequency: int = Field(default=86400, env="LLM_ANALYSIS_FREQUENCY")
    performance_review_frequency: int = Field(default=604800, env="PERFORMANCE_REVIEW_FREQUENCY")
    
    # Safety parameters for US users (when testnet is not available)
    safe_mode: bool = Field(default=True, env="SAFE_MODE")
    safe_max_trade_amount: float = Field(default=10.0, env="SAFE_MAX_TRADE_AMOUNT")
    
    model_config = {"env_file": ".env", "extra": "ignore"}

class BinanceConfig(BaseSettings):
    """Binance.US API configuration (for US users)"""
    binance_api_key: str = Field(env="BINANCE_API_KEY")
    binance_secret_key: str = Field(env="BINANCE_SECRET_KEY")
    binance_testnet: bool = Field(default=True, env="BINANCE_TESTNET")
    
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    @property
    def api_key(self) -> str:
        return self.binance_api_key
    
    @property
    def secret_key(self) -> str:
        return self.binance_secret_key
    
    @property
    def testnet(self) -> bool:
        return self.binance_testnet

class OpenAIConfig(BaseSettings):
    """OpenAI API configuration"""
    openai_api_key: str = Field(env="OPENAI_API_KEY")
    model: str = Field(default="gpt-5")
    
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    @property
    def api_key(self) -> str:
        return self.openai_api_key

class PineconeConfig(BaseSettings):
    """Pinecone configuration"""
    pinecone_api_key: str = Field(env="PINECONE_API_KEY")
    index_name: str = Field(default="evolving-trader-memory")
    
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    @property
    def api_key(self) -> str:
        return self.pinecone_api_key

class DatabaseConfig(BaseSettings):
    """Database configuration"""
    neon_database_url: str = Field(env="NEON_DATABASE_URL")
    
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    @property
    def url(self) -> str:
        return self.neon_database_url

class RedisConfig(BaseSettings):
    """Redis configuration"""
    redis_url: str = Field(env="REDIS_URL")
    upstash_redis_rest_url: str = Field(env="UPSTASH_REDIS_REST_URL")
    upstash_redis_rest_token: str = Field(env="UPSTASH_REDIS_REST_TOKEN")
    
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    @property
    def url(self) -> str:
        return self.redis_url
    
    @property
    def upstash_rest_url(self) -> str:
        return self.upstash_redis_rest_url
    
    @property
    def upstash_rest_token(self) -> str:
        return self.upstash_redis_rest_token

# Global configuration instances
trading_config = TradingConfig()
binance_config = BinanceConfig()
openai_config = OpenAIConfig()
pinecone_config = PineconeConfig()
database_config = DatabaseConfig()
redis_config = RedisConfig()