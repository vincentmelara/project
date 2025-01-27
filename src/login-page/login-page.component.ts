import { Component } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { PasswordModule } from 'primeng/password';
import { FormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { FloatLabelModule } from 'primeng/floatlabel';
import { RippleModule } from 'primeng/ripple';
import { PrimeNGConfig } from 'primeng/api';
import { Router } from '@angular/router';
import { ImageModule } from 'primeng/image';

import { FirebaseService } from '../firebase.service';
import { signInWithEmailAndPassword } from 'firebase/auth';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [
    ButtonModule,
    PasswordModule,
    FormsModule,
    InputTextModule,
    FloatLabelModule,
    RippleModule,
    ImageModule
  ],
  templateUrl: './login-page.component.html',
  styleUrl: './login-page.component.css'
})
export class LoginPageComponent {
  value!: string;

  email: string = '';
  password: string = '';
  errorMessage: string = '';

  constructor(
    private primengConfig: PrimeNGConfig,
    private router: Router,
    private firebaseService: FirebaseService
  ) {}

    ngOnInit() {
        this.primengConfig.ripple = true;
    }
    goToDash() {
      setTimeout(() => {
        this.router.navigate(['/dashboard']);
      }, 300); // Delay of 2 seconds (2000 ms)
    }
    
    async login() {
      try {
        const userCredential = await signInWithEmailAndPassword(
          this.firebaseService.auth,
          this.email,
          this.password
        );
        console.log('User logged in:', userCredential);
  
        // Navigate to the dashboard on successful login
        this.router.navigate(['/dashboard']);
      } catch (error) {
        this.errorMessage = 'Invalid credentials. Please try again.';
        console.error('Login error:', error);
      }
    }
}
