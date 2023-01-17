## Auto-generation of client libraries
Client Libraries are automatically generated on a push to the develop branch. 

1. Typescript Axios => https://github.com/codelorhd/regnify-api-ts-client
2. Dart Dio => https://github.com/codelorhd/regnify-api-dart-dio-client
3. Dart => https://github.com/codelorhd/regnify-api-dart-client
4. Python => https://github.com/codelorhd/regnify-api-python-client

## Requirements
- Edit the names of the right repository to be used for each client library. 
- Replace `codelorhd` with `<GithubProductName>`
- Replace `regnify-api` with `<ProductName>`
- The workflow expects these libraries' repository already created before it is ran.