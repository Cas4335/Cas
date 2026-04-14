"""
PHX Trainer Scaffold — NOT required for v1 runtime.

This is a placeholder for a future fine-tuning workflow.
The trainer is isolated from the production stack and must be
explicitly activated with: --profile training

This service has NO access to phx-postgres, phx-qdrant, or phx-api.
It is a batch job, not a long-running service.
"""

import structlog

logger = structlog.get_logger(__name__)


def main():
    logger.info("trainer_scaffold_placeholder",
                message="Fine-tuning workflow not yet implemented. "
                        "This is a v1 scaffold only.")


if __name__ == "__main__":
    main()
