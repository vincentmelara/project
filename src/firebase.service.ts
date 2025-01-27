import { Injectable } from '@angular/core';
import { initializeApp } from 'firebase/app';
import { getAuth, Auth } from 'firebase/auth';
import { environment } from './environments/environment';

@Injectable({
  providedIn: 'root',
})
export class FirebaseService {
  app = initializeApp(environment.firebase);
  auth: Auth;

  constructor() {
    this.auth = getAuth(this.app);
    console.log('Firebase initialized');
  }
}
