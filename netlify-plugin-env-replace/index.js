const fs = require('fs');
const path = require('path');

module.exports = {
  onBuild: async ({ inputs, utils }) => {
    try {
      // Read the env.js file
      const envPath = path.join(process.cwd(), 'env.js');
      let envContent = fs.readFileSync(envPath, 'utf8');

      // Replace the placeholder with the actual environment variable
      envContent = envContent.replace(
        '{{SHEETDB_API_URL}}',
        process.env.SHEETDB_API_URL || ''
      );

      // Write the modified content back
      fs.writeFileSync(envPath, envContent);

      utils.status.show({
        summary: 'Environment variables injected successfully',
      });
    } catch (error) {
      utils.build.failBuild('Failed to inject environment variables', { error });
    }
  },
}; 