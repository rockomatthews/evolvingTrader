"""
Configuration management for EvolvingTrader
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field
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
    
    class Config:
        env_file = ".env"

class BinanceConfig(BaseSettings):
    """Binance API configuration"""
    api_key: str = Field(env="BINANCE_API_KEY")
    secret_key: str = Field(env="BINANCE_SECRET_KEY")
    testnet: bool = Field(default=True, env="BINANCE_TESTNET")
    
    class Config:
        env_file = ".env"

class OpenAIConfig(BaseSettings):
    """OpenAI API configuration"""
    api_key: str = Field(env="OPENAI_API_KEY")
    model: str = Field(default="gpt-5")
    
    class Config:
        env_file = ".env"

class PineconeConfig(BaseSettings):
    """Pinecone configuration"""
    api_key: str = Field(env="PINECONE_API_KEY")
    index_name: str = Field(default="evolving-trader-memory")
    
    class Config:
        env_file = ".env"

class DatabaseConfig(BaseSettings):
    """Database configuration"""
    url: str = Field(env="NEON_DATABASE_URL")
    
    class Config:
        env_file = ".env"

class RedisConfig(BaseSettings):
    """Redis configuration"""
    url: str = Field(env="REDIS_URL")
    upstash_rest_url: str = Field(env="UPSTASH_REDIS_REST_URL")
    upstash_rest_token: str = Field(env="UPSTASH_REDIS_REST_TOKEN")
    
    class Config:
        env_file = ".env"

# Global configuration instances
trading_config = TradingConfig()
binance_config = BinanceConfig()
openai_config = OpenAIConfig()
pinecone_config = PineconeConfig()
database_config = DatabaseConfig()
redis_config = RedisConfig()