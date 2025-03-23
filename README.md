# SurfAI

## Prerequisites
Before setting up SurfAI, ensure you have the following installed:
- **Node.js** (LTS version recommended)
- **npm** or **yarn**
- **Google Chrome** (for testing the extension)
- **Firebase account** (if using Firestore for storage)
- **Gemini API key** (for AI-powered features)

## Installation

### 1. Clone the Repository
```sh
git clone https://github.com/your-repo/surfai.git
cd surfai
```

### 2. Install Dependencies
```sh
npm install
```

## Configuration

### 3. Set Up Firebase
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/).
2. Enable Firestore and obtain your Firebase config.
3. Update `firebaseConfig.ts` with your Firebase credentials:
```ts
import { initializeApp } from "firebase/app";
import { getFirestore, collection } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID",
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
export const chatCollection = collection(db, "chats");
export { db };
```

### 4. Set Up Gemini API Key
1. Get an API key from Google Gemini.
2. Create an `.env` file in the project root and add:
```sh
REACT_APP_GEMINI_API_KEY=your_api_key_here
```

## Running SurfAI Locally

### 5. Build and Load the Extension
1. Run:
   ```sh
   npm run build
   ```
2. Open **Google Chrome** and go to `chrome://extensions/`
3. Enable **Developer Mode** (top right corner).
4. Click **Load Unpacked** and select the `build` folder.

### 6. Start the Development Server (Optional)
If using a backend service:
```sh
npm start
```

## Deployment
For a production build:
```sh
npm run build
```
Then, package and submit to the **Chrome Web Store** or host manually.

## Troubleshooting
- **API Errors:** Check if the API key is valid and added in `.env`.
- **Firebase Issues:** Ensure Firestore is enabled and security rules are configured.
- **Extension Not Loading:** Verify `chrome://extensions/` settings and check the browser console for errors.

---

SurfAI is now ready to enhance your browsing experience! 🚀

