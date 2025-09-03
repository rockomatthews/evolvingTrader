"""
Pinecone vector database client for long-term memory and strategy evolution
"""
import asyncio
import json
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
import hashlib

try:
    from pinecone import Pinecone
except ImportError:
    try:
        # Try different import patterns
        import pinecone
        if hasattr(pinecone, 'Pinecone'):
            Pinecone = pinecone.Pinecone
        elif hasattr(pinecone, 'init'):
            # Older version
            class PineconeWrapper:
                def __init__(self, api_key, environment=None):
                    self.api_key = api_key
                    self.environment = environment
                    pinecone.init(api_key=api_key, environment=environment)
                
                def Index(self, index_name):
                    return pinecone.Index(index_name)
                
                def list_indexes(self):
                    return pinecone.list_indexes()
                
                def create_index(self, name, dimension, metric="cosine", spec=None):
                    return pinecone.create_index(name, dimension, metric, spec)
                
                def describe_index(self, name):
                    return pinecone.describe_index(name)
            
            Pinecone = PineconeWrapper
        else:
            raise ImportError("Cannot find Pinecone class")
    except Exception as e:
        print(f"Warning: Pinecone import failed: {e}")
        # Create a dummy class for testing
        class DummyPinecone:
            def __init__(self, *args, **kwargs):
                pass
            def Index(self, *args, **kwargs):
                return DummyIndex()
        
        class DummyIndex:
            def upsert(self, *args, **kwargs):
                return {'upserted_count': 0}
            def query(self, *args, **kwargs):
                return {'matches': []}
        
        Pinecone = DummyPinecone
from config import pinecone_config

logger = logging.getLogger(__name__)

@dataclass
class MemoryRecord:
    """Structure for storing memory records"""
    id: str
    vector: List[float]
    metadata: Dict[str, Any]
    timestamp: datetime
    record_type: str  # 'trade', 'performance', 'strategy_params', 'market_pattern'

class PineconeMemoryClient:
    """
    Pinecone client for storing and retrieving trading strategy memory
    """
    
    def __init__(self):
        self.pc: Optional[Pinecone] = None
        self.index = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize Pinecone connection and index"""
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=pinecone_config.api_key)
            
            # Check if index exists, create if not
            if pinecone_config.index_name not in self.pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {pinecone_config.index_name}")
                
                self.pc.create_index(
                    name=pinecone_config.index_name,
                    dimension=512,  # Dimension for embeddings
                    metric="cosine",
                    spec={
                        "serverless": {
                            "cloud": "aws",
                            "region": "us-east-1"
                        }
                    }
                )
                
                # Wait for index to be ready
                while not self.pc.describe_index(pinecone_config.index_name).status['ready']:
                    await asyncio.sleep(1)
            
            # Connect to index
            self.index = self.pc.Index(pinecone_config.index_name)
            self.initialized = True
            
            logger.info("Pinecone memory client initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using simple hash-based approach"""
        # For production, you'd use a proper embedding model like OpenAI's text-embedding-ada-002
        # This is a simplified version for demonstration
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 512-dimensional vector
        vector = []
        for i in range(0, len(hash_bytes), 2):
            if i + 1 < len(hash_bytes):
                # Combine two bytes and normalize
                val = (hash_bytes[i] << 8) + hash_bytes[i + 1]
                vector.append(val / 65535.0)  # Normalize to [0, 1]
        
        # Pad or truncate to exactly 512 dimensions
        while len(vector) < 512:
            vector.append(0.0)
        vector = vector[:512]
        
        return vector
    
    def _create_record_id(self, record_type: str, data: Dict) -> str:
        """Create unique ID for record"""
        # Create deterministic ID based on record type and key data
        if record_type == 'trade':
            key_data = f"{data.get('symbol', '')}_{data.get('timestamp', '')}"
        elif record_type == 'strategy_params':
            key_data = f"params_{data.get('timestamp', '')}"
        elif record_type == 'performance':
            key_data = f"perf_{data.get('timestamp', '')}"
        else:
            key_data = f"{record_type}_{data.get('timestamp', '')}"
        
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def store_trade_record(self, trade_data: Dict):
        """Store a trade record in memory"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Create embedding from trade data
            trade_text = f"Trade: {trade_data['symbol']} {trade_data['side']} " \
                        f"Entry: {trade_data['entry_price']} Exit: {trade_data['exit_price']} " \
                        f"P&L: {trade_data['pnl']} Reason: {trade_data['reason']}"
            
            vector = self._generate_embedding(trade_text)
            
            # Create record
            record_id = self._create_record_id('trade', trade_data)
            
            metadata = {
                'record_type': 'trade',
                'symbol': trade_data['symbol'],
                'side': trade_data['side'],
                'entry_price': trade_data['entry_price'],
                'exit_price': trade_data['exit_price'],
                'quantity': trade_data['quantity'],
                'pnl': trade_data['pnl'],
                'reason': trade_data['reason'],
                'reasoning': trade_data.get('reasoning', ''),
                'timestamp': trade_data['timestamp'].isoformat(),
                'trade_text': trade_text
            }
            
            # Store in Pinecone
            self.index.upsert([(record_id, vector, metadata)])
            
            logger.debug(f"Stored trade record: {record_id}")
            
        except Exception as e:
            logger.error(f"Failed to store trade record: {e}")
    
    async def store_strategy_parameters(self, params: Dict, reasoning: str = ""):
        """Store strategy parameters in memory"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Create embedding from parameters and reasoning
            params_text = f"Strategy Parameters: {json.dumps(params)} Reasoning: {reasoning}"
            vector = self._generate_embedding(params_text)
            
            # Create record
            record_id = self._create_record_id('strategy_params', {'timestamp': datetime.now()})
            
            metadata = {
                'record_type': 'strategy_params',
                'timestamp': datetime.now().isoformat(),
                'reasoning': reasoning,
                'params_text': params_text,
                **params  # Include all parameters
            }
            
            # Store in Pinecone
            self.index.upsert([(record_id, vector, metadata)])
            
            logger.info(f"Stored strategy parameters: {record_id}")
            
        except Exception as e:
            logger.error(f"Failed to store strategy parameters: {e}")
    
    async def store_performance_summary(self, performance_data: Dict):
        """Store performance summary in memory"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Create embedding from performance data
            perf_text = f"Performance: Trades: {performance_data.get('total_trades', 0)} " \
                       f"P&L: {performance_data.get('total_pnl', 0)} " \
                       f"Win Rate: {performance_data.get('win_rate', 0)}%"
            
            vector = self._generate_embedding(perf_text)
            
            # Create record
            record_id = self._create_record_id('performance', {'timestamp': datetime.now()})
            
            metadata = {
                'record_type': 'performance',
                'timestamp': datetime.now().isoformat(),
                'perf_text': perf_text,
                **performance_data
            }
            
            # Store in Pinecone
            self.index.upsert([(record_id, vector, metadata)])
            
            logger.debug(f"Stored performance summary: {record_id}")
            
        except Exception as e:
            logger.error(f"Failed to store performance summary: {e}")
    
    async def store_market_pattern(self, pattern_data: Dict):
        """Store market pattern in memory"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Create embedding from pattern data
            pattern_text = f"Market Pattern: {pattern_data.get('description', '')} " \
                          f"Symbol: {pattern_data.get('symbol', '')} " \
                          f"Conditions: {pattern_data.get('conditions', '')}"
            
            vector = self._generate_embedding(pattern_text)
            
            # Create record
            record_id = self._create_record_id('market_pattern', pattern_data)
            
            metadata = {
                'record_type': 'market_pattern',
                'timestamp': datetime.now().isoformat(),
                'pattern_text': pattern_text,
                **pattern_data
            }
            
            # Store in Pinecone
            self.index.upsert([(record_id, vector, metadata)])
            
            logger.debug(f"Stored market pattern: {record_id}")
            
        except Exception as e:
            logger.error(f"Failed to store market pattern: {e}")
    
    async def query_similar_trades(self, query_text: str, limit: int = 10) -> List[Dict]:
        """Query for similar trades based on text description"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Generate query embedding
            query_vector = self._generate_embedding(query_text)
            
            # Query Pinecone
            results = self.index.query(
                vector=query_vector,
                top_k=limit,
                filter={'record_type': 'trade'},
                include_metadata=True
            )
            
            return [match['metadata'] for match in results['matches']]
            
        except Exception as e:
            logger.error(f"Failed to query similar trades: {e}")
            return []
    
    async def query_strategy_parameters(self, limit: int = 5) -> List[Dict]:
        """Query for recent strategy parameters"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Query for strategy parameters
            results = self.index.query(
                vector=[0.0] * 512,  # Dummy vector
                top_k=limit,
                filter={'record_type': 'strategy_params'},
                include_metadata=True
            )
            
            return [match['metadata'] for match in results['matches']]
            
        except Exception as e:
            logger.error(f"Failed to query strategy parameters: {e}")
            return []
    
    async def query_performance_history(self, limit: int = 50) -> List[Dict]:
        """Query for performance history"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Query for performance records
            results = self.index.query(
                vector=[0.0] * 512,  # Dummy vector
                top_k=limit,
                filter={'record_type': 'performance'},
                include_metadata=True
            )
            
            return [match['metadata'] for match in results['matches']]
            
        except Exception as e:
            logger.error(f"Failed to query performance history: {e}")
            return []
    
    async def query_market_patterns(self, symbol: str = None, limit: int = 10) -> List[Dict]:
        """Query for market patterns"""
        if not self.initialized:
            await self.initialize()
        
        try:
            filter_dict = {'record_type': 'market_pattern'}
            if symbol:
                filter_dict['symbol'] = symbol
            
            # Query for market patterns
            results = self.index.query(
                vector=[0.0] * 512,  # Dummy vector
                top_k=limit,
                filter=filter_dict,
                include_metadata=True
            )
            
            return [match['metadata'] for match in results['matches']]
            
        except Exception as e:
            logger.error(f"Failed to query market patterns: {e}")
            return []
    
    async def analyze_pattern_effectiveness(self, pattern_type: str) -> Dict:
        """Analyze effectiveness of specific patterns"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Query for patterns of specific type
            results = self.index.query(
                vector=[0.0] * 512,
                top_k=100,
                filter={'record_type': 'market_pattern', 'pattern_type': pattern_type},
                include_metadata=True
            )
            
            if not results['matches']:
                return {'pattern_type': pattern_type, 'effectiveness': 0.0, 'sample_size': 0}
            
            # Analyze effectiveness (simplified)
            total_patterns = len(results['matches'])
            successful_patterns = sum(1 for match in results['matches'] 
                                    if match['metadata'].get('success', False))
            
            effectiveness = successful_patterns / total_patterns if total_patterns > 0 else 0
            
            return {
                'pattern_type': pattern_type,
                'effectiveness': effectiveness,
                'sample_size': total_patterns,
                'successful_patterns': successful_patterns
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze pattern effectiveness: {e}")
            return {'pattern_type': pattern_type, 'effectiveness': 0.0, 'sample_size': 0}
    
    async def get_memory_statistics(self) -> Dict:
        """Get statistics about stored memory"""
        if not self.initialized:
            await self.initialize()
        
        try:
            stats = self.index.describe_index_stats()
            
            # Count records by type
            record_counts = {}
            for record_type in ['trade', 'strategy_params', 'performance', 'market_pattern']:
                try:
                    results = self.index.query(
                        vector=[0.0] * 512,
                        top_k=1,
                        filter={'record_type': record_type},
                        include_metadata=False
                    )
                    record_counts[record_type] = len(results['matches'])
                except:
                    record_counts[record_type] = 0
            
            return {
                'total_vectors': stats.total_vector_count,
                'dimension': stats.dimension,
                'record_counts': record_counts,
                'index_name': pinecone_config.index_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory statistics: {e}")
            return {}
    
    async def cleanup_old_records(self, days_to_keep: int = 30):
        """Clean up old records to manage storage costs"""
        if not self.initialized:
            await self.initialize()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # This is a simplified cleanup - in production you'd want more sophisticated logic
            logger.info(f"Cleanup would remove records older than {cutoff_date}")
            # Implementation would depend on Pinecone's delete capabilities
            
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {e}")