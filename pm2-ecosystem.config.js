const path = require('path');
const projectDir = path.dirname(__filename);

const pm2EcosystemConfig = {
    apps: [
       {
           name: `${path.basename(projectDir)}-api`,
           cwd: path.resolve(projectDir, './'),
           script: path.resolve(projectDir, './scripts/pm2/run_api.sh'),
           watch: false,
           exec_mode: 'fork',
           env: {
               "PROJECT_DIR": projectDir,
               "DJANGO_CONFIGURATION": "Development",
               "GUNICORN_TIMEOUT": 30,
           },
           env_development: {
               "DJANGO_CONFIGURATION": "Development",
               "GUNICORN_TIMEOUT": 60,
           },
           env_staging: {
               "DJANGO_CONFIGURATION": "Staging",
               "GUNICORN_TIMEOUT": 60,
           },
           env_production: {
               "DJANGO_CONFIGURATION": "Production",
               "GUNICORN_TIMEOUT": 120,
           },
       },
        {
            name: `${path.basename(projectDir)}-celery`,
            cwd: path.resolve(projectDir, './'),
            script: path.resolve(projectDir, './scripts/pm2/run_celery.sh'),
            watch: false,
            exec_mode: 'fork',
            env: {
                "PROJECT_DIR": projectDir,
                "DJANGO_CONFIGURATION": "Development"
            },
            env_development: {
                "DJANGO_CONFIGURATION": "Development"
            },
            env_staging: {
                "DJANGO_CONFIGURATION": "Staging"
            },
            env_production: {
                "DJANGO_CONFIGURATION": "Production"
            },
        },
        {
            name: `${path.basename(projectDir)}-celerybeat`,
            cwd: path.resolve(projectDir, './'),
            script: path.resolve(projectDir, './scripts/pm2/run_celerybeat.sh'),
            watch: false,
            exec_mode: 'fork',
            env: {
                "PROJECT_DIR": projectDir,
                "DJANGO_CONFIGURATION": "Development"
            },
            env_development: {
                "DJANGO_CONFIGURATION": "Development"
            },
            env_staging: {
                "DJANGO_CONFIGURATION": "Staging"
            },
            env_production: {
                "DJANGO_CONFIGURATION": "Production"
            },
        },
    ],
};

console.log(`PM2 Ecosystem config : ${JSON.stringify(pm2EcosystemConfig)}`);
module.exports = pm2EcosystemConfig;
