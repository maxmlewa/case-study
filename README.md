# Instalily AI Case Study - PartSelect Chat Agent

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Overview
This project implements a focused, production style chat agent for the PartSelect e-commerce experience, limited to refrigerator and dishwasher parts.

The agent helps users:
- find parts
- check compatibility with appliance models
- find installation guides
- troubleshoot common appliance issues
- get basic support regarding orders

My focus for this project was correctness, clarity, and extensibility thus the need to maintain a small set of seeded data and follow deterministic workflows.


## Architecture Summary

The system uses a deterministic agent core with LLM augmentation for language quality.


```
React (CRA) Frontend
        |
FastAPI Backend
        |
        +-- Intent Detection (rules)
        +-- Scope Guard (hard limits)
        +-- Deterministic Knowledge
        |     - Parts seed
        |     - Compatibility table
        |     - Installation guides
        |     - Troubleshooting flows
        |
        +-- LLM (optional, using Gemini)
              - Rewrite responses for clarity
              - Fallback clarifying question only
```

### Reasons for this design
- the deterministic nature means that the agent will stick to the facts and made debugging easier
- the LLM is secondary so that the user experience can be improved without compromising the facts
- every answer can be traced back to a data source (using seeds as of now)


## Frontend

The framework used is the Create React App from the provided template.\
Key features:
- Chat user interface with message history
- The production cards (product images and descriptions) are rendered inline
- There are 2 actions buttons for installation and compatibility checks and a redirect link to the PartSelect website

## Backend







In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
