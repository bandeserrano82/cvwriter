# Skill Report: email-services

Scanned 233 files. Detected 5 languages, 3 frameworks/tools, and 5 broader engineering capabilities.

## Languages

- **JavaScript** (n/a confidence, 76 evidence)

- **JSON** (n/a confidence, 56 evidence)

- **YAML** (n/a confidence, 14 evidence)

- **SQL** (n/a confidence, 8 evidence)

- **HTML** (n/a confidence, 1 evidence)

## Frameworks And Tools

- **Azure** (high confidence, 3 evidence)
  Evidence: `email-services\ai-worker-functions\package.json, email-services\package.json, email-services\webhook-handler\package.json`

- **Express** (high confidence, 3 evidence)
  Evidence: `email-services\ai-tasks-manager-backend\package.json, email-services\webapp-agent\package.json, email-services\webhook-handler\package.json`

- **Prisma** (medium confidence, 2 evidence)
  Evidence: `email-services\ai-tasks-manager-backend\package.json`

## Engineering Capabilities

- **Authentication** (high confidence, 18 evidence)
  Evidence: `email-services\ai-tasks-manager-backend\src\controllers\brokerInboxPlaceholderController.js, email-services\ai-worker-functions\src\agentsconfig\broker-inbox\supplier_response_processing_tools.js, email-services\ai-worker-functions\src\agentsconfig\sample-agent\sample-agent-tools.js, email-services\common\tasks\agents_workflows\sparkplugHelpers.js, email-services\common\tasks\notifyHelpers.js`

- **Containerization** (high confidence, 4 evidence)
  Evidence: `email-services\ai-worker-functions\src\agentsconfig\craft\craft_bot_tools.js, email-services\ai-worker-functions\src\agentsconfig\propeller\propeller_info_bot_tools.js, email-services\webapp-agent\aiResponseControllers\craftResponseController.js, email-services\webapp-agent\aiResponseControllers\propellerInfoController.js`

- **Database Design** (high confidence, 63 evidence)
  Evidence: `email-services\ai-tasks-manager-backend\prisma\migrations\20251208205646_initial_migration\migration.sql, email-services\ai-tasks-manager-backend\prisma\migrations\20260512113000_add_internal_users_and_grants\migration.sql, email-services\ai-tasks-manager-backend\src\controllers\flowsController.js, email-services\ai-tasks-manager-backend\src\controllers\tasksController.js, email-services\ai-tasks-manager-backend\src\index.js`

- **REST APIs** (high confidence, 66 evidence)
  Evidence: `email-services\ai-tasks-manager-backend\src\index.js, email-services\ai-tasks-manager-backend\src\routes\brokerInboxPlaceholderRoutes.js, email-services\ai-tasks-manager-backend\src\routes\flowsRoutes.js, email-services\ai-tasks-manager-backend\src\routes\internalUsersRoutes.js, email-services\ai-tasks-manager-backend\src\routes\tasksRoutes.js`

- **Testing** (high confidence, 9 evidence)
  Evidence: `email-services\ai-tasks-manager-backend\src\controllers\brokerInboxPlaceholderController.js, email-services\ai-worker-functions\src\agentsconfig\broker-inbox\supplier_response_processing_tools.js, email-services\ai-worker-functions\src\execAgent.js, email-services\common\tasks\agents_workflows\sparkplugHelpers.js, email-services\common\tasks\attachmentHelper.js`