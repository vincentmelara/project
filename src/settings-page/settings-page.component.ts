import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-settings-page',
  standalone: true,
  imports: [],
  templateUrl: './settings-page.component.html',
  styleUrl: './settings-page.component.css'
})
export class SettingsPageComponent {
  constructor(
    private router: Router
  ){

  }
  logout() {
    // Perform logout functionality here
    console.log('Logout button clicked');
    // Example: Redirect to the login page
    this.router.navigate(['/login']);
  }
}
