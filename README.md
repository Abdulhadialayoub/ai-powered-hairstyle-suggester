# AI-Powered Hairstyle Suggester (React + Firebase) 💇‍♀️

An intelligent web application that uses computer vision to analyze a user's face shape from a photograph and recommend flattering hairstyles. This project is built on a modern, scalable **serverless architecture**, with a frontend powered by **React** and **Vite**.

![Application Interface Screenshot](https://i.imgur.com/your-app-screenshot.png)
---

## ✨ Core Features

-   🤖 **AI-Powered Face Analysis**: Automatically classifies the user's face shape (e.g., Oval, Square, Round) using **OpenCV** and **Dlib**.
-   ✨ **Personalized Recommendations**: Suggests a curated list of hairstyles best suited for the identified face shape.
-   👤 **Secure User Authentication**: A robust user registration and login system powered by **Firebase Authentication** using email and password.
-   ❤️ **Favorites System**: Allows users to save their favorite hairstyle suggestions to their personal profile for future reference.
-   ⚡ **Modern Frontend**: A fast, dynamic, and interactive user interface built with **React** and bundled with **Vite**.
-   ☁️ **Fully Serverless Architecture**: A scalable infrastructure running entirely on Google Firebase, eliminating the need for traditional server management.

---

## 🛠️ Tech Stack

This project integrates a range of modern technologies to provide a full-stack, serverless application experience.

### **Frontend (Client-Side)**
-   **React**: A component-based JavaScript library for building user interfaces.
-   **Vite**: A next-generation frontend tooling that provides an extremely fast development server and optimized build processes.
-   **JSX**: A syntax extension for JavaScript used with React to describe what the UI should look like.
-   **CSS Modules / Tailwind CSS**: For component-scoped styling.
-   **Firebase Web SDK**: The library that enables the React application to communicate with Firebase services.

### **Backend (Serverless Services)**
-   **Firebase Authentication**: For handling user identity and authentication.
-   **Cloud Firestore**: A NoSQL database for storing user data, analysis results, and favorites.
-   **Cloud Storage for Firebase**: For securely storing user-uploaded photos.
-   **Cloud Functions for Firebase**: For running the serverless backend logic, including the AI analysis.

### **AI / Computer Vision** (within the Cloud Function)
-   **Python 3.9**: The runtime environment for the analysis script.
-   **OpenCV**: For face detection.
-   **Dlib**: For extracting facial landmarks.

### **Tools & Deployment**
-   **Git & GitHub**: For version control.
-   **Node.js & npm**: For JavaScript package management.
-   **Firebase CLI**: For deploying the application and local testing.

---

## 🚀 Setup and Local Development

Follow these steps to run the project on your local machine.

### **Prerequisites**
-   [Node.js](https://nodejs.org/) (v16+ recommended)
-   [Python 3.9+](https://www.python.org/)
-   [Firebase CLI](https://firebase.google.com/docs/cli):
    ```bash
    npm install -g firebase-tools
    ```

### **Installation Steps**

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/Abdulhadialayoub/ai-powered-hairstyle-suggester.git](https://github.com/Abdulhadialayoub/ai-powered-hairstyle-suggester.git)
    cd ai-powered-hairstyle-suggester
    ```

2.  **Set Up Your Firebase Project:**
    -   Go to the [Firebase Console](https://console.firebase.google.com/) and create a new project.
    -   Enable **Authentication** (with the Email/Password method), **Firestore**, and **Storage**.
    -   Upgrade your project to the **Blaze (Pay-as-you-go)** plan. This is required to use Cloud Functions with Python, but your usage for a class project will almost certainly stay within the free tier.

3.  **Connect Your Local Project to Firebase:**
    ```bash
    firebase login
    firebase use --add
    ```
    > From the list, select the Firebase Project ID you just created.

4.  **Frontend Setup:**
    -   Navigate to your React app directory (e.g., `cd frontend` or the project root).
    -   Install the necessary npm packages:
        ```bash
        npm install
        ```
    -   Create a `.env` file in the root of your frontend project and add your Firebase configuration details, which you can find in your Firebase project settings:
        ```env
        VITE_FIREBASE_API_KEY="your-api-key"
        VITE_FIREBASE_AUTH_DOMAIN="your-auth-domain"
        VITE_FIREBASE_PROJECT_ID="your-project-id"
        VITE_FIREBASE_STORAGE_BUCKET="your-storage-bucket"
        VITE_FIREBASE_MESSAGING_SENDER_ID="your-sender-id"
        VITE_FIREBASE_APP_ID="your-app-id"
        ```

5.  **Backend (Cloud Functions) Setup:**
    -   Inside the `functions` directory, add the required Python libraries to the `requirements.txt` file:
        ```txt
        opencv-python-headless
        dlib
        numpy
        firebase-admin
        google-cloud-storage
        ```

6.  **Start the Local Development Server:**
    -   To run the frontend live, start the Vite development server:
        ```bash
        npm run dev
        ```
    -   Open your browser to `http://localhost:5173` (or the port specified by Vite).
    > **Note:** To test Cloud Functions locally, it is highly recommended to use the **Firebase Emulator Suite**: `firebase emulators:start`

### **Deployment**

1.  **Build the React Application:**
    -   Run the build command to compile your frontend code into optimized static files. This will create a `dist` folder.
        ```bash
        npm run build
        ```

2.  **Deploy to Firebase:**
    -   Ensure your `firebase.json` file is configured to point to the `dist` folder for hosting:
        ```json
        {
          "hosting": {
            "public": "dist",
            "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
            "rewrites": [{
              "source": "**",
              "destination": "/index.html"
            }]
          }
        }
        ```
    -   Finally, deploy your website and cloud functions to the live environment:
        ```bash
        firebase deploy
        ```

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
