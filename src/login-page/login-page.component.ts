import { Component } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { PasswordModule } from 'primeng/password';
import { FormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { FloatLabelModule } from 'primeng/floatlabel';
import { RippleModule } from 'primeng/ripple';
import { PrimeNGConfig } from 'primeng/api';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [
    ButtonModule,
    PasswordModule,
    FormsModule,
    InputTextModule,
    FloatLabelModule,
    RippleModule
  ],
  templateUrl: './login-page.component.html',
  styleUrl: './login-page.component.css'
})
export class LoginPageComponent {
  value!: string;
  constructor(
    private primengConfig: PrimeNGConfig,
    private router: Router
  ) {}

    ngOnInit() {
        this.primengConfig.ripple = true;
    }
    goToDash() {
      this.router.navigate(['/dashboard']);
    }
}
