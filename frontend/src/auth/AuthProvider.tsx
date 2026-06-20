/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { onAuthStateChanged, type User } from 'firebase/auth';
import { auth, signInWithEmail, signInWithGoogle, signOutCurrentUser, signUpWithEmail } from './firebase';

interface AuthContextValue {
  user: User | null;
  isAuthLoading: boolean;
  signInGoogle: () => Promise<void>;
  signInEmail: (email: string, password: string) => Promise<void>;
  signUpEmail: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  useEffect(() => {
    return onAuthStateChanged(auth, nextUser => {
      setUser(nextUser);
      setIsAuthLoading(false);
    });
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    isAuthLoading,
    signInGoogle: async () => {
      await signInWithGoogle();
    },
    signInEmail: async (email, password) => {
      await signInWithEmail(email, password);
    },
    signUpEmail: async (email, password) => {
      await signUpWithEmail(email, password);
    },
    logout: signOutCurrentUser,
  }), [isAuthLoading, user]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
