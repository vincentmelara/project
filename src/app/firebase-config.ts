import { initializeApp } from 'firebase/app';
import { getAnalytics } from 'firebase/analytics';
import { environment } from '../environments/environment';

// Initialize Firebase
export const app = initializeApp(environment.firebase);
export const analytics = getAnalytics(app);
