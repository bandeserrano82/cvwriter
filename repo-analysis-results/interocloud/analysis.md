# Skill Report: interocloud

Scanned 1108 files. Detected 12 languages, 9 frameworks/tools, and 5 broader engineering capabilities.

## Languages

- **PHP** (n/a confidence, 425 evidence)

- **HTML** (n/a confidence, 191 evidence)

- **Vue** (n/a confidence, 67 evidence)

- **JavaScript** (n/a confidence, 64 evidence)

- **Less** (n/a confidence, 32 evidence)

- **JSON** (n/a confidence, 25 evidence)

- **CSS** (n/a confidence, 21 evidence)

- **SCSS** (n/a confidence, 4 evidence)

- **YAML** (n/a confidence, 3 evidence)

- **SQL** (n/a confidence, 2 evidence)

- **Docker** (n/a confidence, 1 evidence)

- **TypeScript** (n/a confidence, 1 evidence)

## Frameworks And Tools

- **Bootstrap** (medium confidence, 2 evidence)
  Evidence: `frontend\package.json, interocloud_web\package.json`

- **Docker Compose** (medium confidence, 2 evidence)
  Evidence: `api\docker-compose.yml`

- **ESLint** (low confidence, 1 evidence)
  Evidence: `frontend\package.json`

- **Express** (low confidence, 1 evidence)
  Evidence: `frontend\assets\js\dhtmlx-scheduler\backend\package.json`

- **Jest** (low confidence, 1 evidence)
  Evidence: `interocloud_web\package.json`

- **Nuxt.js** (medium confidence, 2 evidence)
  Evidence: `frontend\package.json, interocloud_web\package.json`

- **Prettier** (low confidence, 1 evidence)
  Evidence: `frontend\package.json`

- **Vue.js** (medium confidence, 2 evidence)
  Evidence: `frontend\package.json, interocloud_web\package.json`

- **Webpack** (medium confidence, 2 evidence)
  Evidence: `frontend\package.json, interocloud_web\package.json`

## Engineering Capabilities

- **Authentication** (high confidence, 277 evidence)
  Evidence: `api\app\Exceptions\Handler.php, api\app\Helpers\InterocloudPathGenerator.php, api\app\Http\Controllers\API\AppSettingsApiController.php, api\app\Http\Controllers\API\AppointmentApiController.php, api\app\Http\Controllers\API\Auth\ForgotPasswordController.php`

- **Containerization** (high confidence, 38 evidence)
  Evidence: `api\app\Console\Commands\RestoreDatabaseSequences.php, api\app\Models\Appointment.php, api\app\Models\PatientSubscription.php, api\app\Models\Service.php, api\app\Reports\FinancialReport.php`

- **Database Design** (high confidence, 400 evidence)
  Evidence: `api\database\migrations\2014_10_12_100000_create_password_resets_table.php, api\database\migrations\2019_08_19_000000_create_failed_jobs_table.php, api\database\migrations\2019_12_14_000001_create_personal_access_tokens_table.php, api\database\migrations\2022_04_11_104732_create_client_types_table.php, api\database\migrations\2022_04_11_124736_create_payment_plans_table.php`

- **REST APIs** (medium confidence, 4 evidence)
  Evidence: `frontend\assets\js\dhtmlx-scheduler\backend\router.js`

- **Testing** (high confidence, 58 evidence)
  Evidence: `InteroCloud_files\clarity.js, api\tests\APIs\AppointmentApiTest.php, api\tests\APIs\PatientPaymentsApiTest.php, api\tests\APIs\PersonnelServicesApiTest.php, api\tests\APIs\Reports\GeneralReportApiTest.php`