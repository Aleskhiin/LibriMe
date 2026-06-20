import { initializeApp } from 'firebase/app';
import {
  createUserWithEmailAndPassword,
  getAuth,
  GoogleAuthProvider,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
} from 'firebase/auth';
import { getRuntimeConfig } from '../runtimeConfig';

const runtimeConfig = getRuntimeConfig();

const firebaseConfig = {
  apiKey: runtimeConfig.firebaseApiKey ?? 'AIzaSyCLS4upLJ1miLntEeh-4Ba9ZhV8_v4KFaw',
  authDomain: runtimeConfig.firebaseAuthDomain ?? 'librime.firebaseapp.com',
  projectId: runtimeConfig.firebaseProjectId ?? 'librime',
  appId: runtimeConfig.firebaseAppId,
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);

const googleProvider = new GoogleAuthProvider();

export function signInWithGoogle() {
  return signInWithPopup(auth, googleProvider);
}

export function signInWithEmail(email: string, password: string) {
  return signInWithEmailAndPassword(auth, email, password);
}

export function signUpWithEmail(email: string, password: string) {
  return createUserWithEmailAndPassword(auth, email, password);
}

export function signOutCurrentUser() {
  return signOut(auth);
}
