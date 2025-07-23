from typing import Optional, Type
from .config import AgentConfiguration
from .llm.base import LLMProvider
from .llm.openai_provider import OpenAIProvider
from .utils.logging import ConsoleAgentLogger
from .utils.galileo_logger import create_galileo_logger
from .agent import Agent
from .awesome_list_agent import AwesomeListAgent
import os

class AgentFactory:
    """Factory for creating agents with proper dependency injection"""
    
    def __init__(self, config: AgentConfiguration):
        self.config = config
        self._llm_provider: Optional[LLMProvider] = None
        self._logger: Optional[ConsoleAgentLogger] = None
    
    def get_llm_provider(self) -> Optional[LLMProvider]:
        """Get or create LLM provider (optional)"""
        if not self._llm_provider:
            if "openai" in self.config.api_keys:
                self._llm_provider = OpenAIProvider(
                    config=self.config.llm_config
                )
            else:
                # Return None if no LLM provider is configured
                return None
        return self._llm_provider
    
    def get_logger(self, agent_id: str) -> Optional[ConsoleAgentLogger]:
        """Get logger if enabled"""
        if self.config.enable_logging:
            return create_galileo_logger(agent_id)
        return None
    
    def create_agent(
        self,
        agent_class: Type[Agent],
        agent_id: Optional[str] = None,
        **kwargs
    ) -> Agent:
        """Create an agent instance with proper dependencies"""
        # Create core dependencies
        llm_provider = self.get_llm_provider()
        logger = self.get_logger(agent_id) if agent_id else None
        
        # Create agent with injected dependencies
        agent = agent_class(
            agent_id=agent_id,
            llm_provider=llm_provider,
            logger=logger,
            verbosity=self.config.verbosity,
            metadata=self.config.metadata,
            **kwargs
        )
        
        return agent


class AwesomeListAgentFactory:
    """Factory specifically for creating AwesomeListAgent instances with Galileo support"""
    
    @classmethod
    async def create_agent(
        cls,
        verbosity: str = "low",
        enable_galileo: bool = None,
        agent_id: Optional[str] = None,
        **kwargs
    ) -> AwesomeListAgent:
        """
        Create an AwesomeListAgent with proper Galileo initialization.
        
        Args:
            verbosity: Logging verbosity level ("low", "medium", "high")
            enable_galileo: Whether to enable Galileo logging (defaults to GALILEO_ENABLED env var)
            agent_id: Optional agent ID
            **kwargs: Additional arguments passed to agent constructor
            
        Returns:
            Configured AwesomeListAgent instance
        """
        # Determine Galileo enablement
        if enable_galileo is None:
            enable_galileo = os.getenv("GALILEO_ENABLED", "false").lower() == "true"
        
        # Create configuration
        from .config import AgentConfiguration, VerbosityLevel
        
        # Map verbosity string to enum
        verbosity_map = {
            "none": VerbosityLevel.NONE,
            "low": VerbosityLevel.LOW,
            "high": VerbosityLevel.HIGH
        }
        verbosity_level = verbosity_map.get(verbosity.lower(), VerbosityLevel.LOW)
        
        config = AgentConfiguration(
            verbosity=verbosity_level,
            enable_logging=enable_galileo,
            api_keys={},  # Will be loaded from environment
            metadata={"agent_type": "awesome_list_agent"}
        )
        
        # Create factory and agent
        factory = AgentFactory(config)
        
        # Generate agent ID if not provided
        if not agent_id:
            import uuid
            agent_id = f"awesome_list_agent_{uuid.uuid4().hex[:8]}"
        
        # Create agent with proper dependencies
        agent = factory.create_agent(
            agent_class=AwesomeListAgent,
            agent_id=agent_id,
            **kwargs
        )
        
        # Log Galileo status
        if enable_galileo:
            print(f"📊 Galileo observability ENABLED for agent {agent_id}")
        else:
            print(f"📊 Galileo observability DISABLED for agent {agent_id}")
        
        return agent 