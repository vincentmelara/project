import { Routes } from '@angular/router';
import { DashboardComponent } from '../dashboard/dashboard.component';
import { LoginPageComponent } from '../login-page/login-page.component';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' }, // Default route redirects to LoginComponent
  { path: 'dashboard', component: DashboardComponent },
  { path: 'login', component: LoginPageComponent },

];

