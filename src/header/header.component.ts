import { ThemeService } from './../services/theme.service';
import { Component, OnInit, inject } from '@angular/core';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { Router } from '@angular/router';
import { ImageModule } from 'primeng/image';
import { InputSwitchModule } from 'primeng/inputswitch';
import { FormsModule } from '@angular/forms';
import { ToolbarModule } from 'primeng/toolbar';
import { InputTextModule } from 'primeng/inputtext';
import { RippleModule } from 'primeng/ripple';
import { PrimeNGConfig } from 'primeng/api';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [
    CardModule,
    ButtonModule,
    ImageModule,
    InputSwitchModule,
    FormsModule,
    ToolbarModule,
    InputTextModule,
    RippleModule
  ],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css'
})
export class HeaderComponent implements OnInit{
  currentTime: string;
  isDarkMode: boolean = true;

  checked: boolean = true;
  selectedTheme: string = 'dark';
  themeService: ThemeService = inject(ThemeService);


  constructor(
    private router: Router,
        private primengConfig: PrimeNGConfig,

  ) {
    this.currentTime = new Date().toLocaleString();

    // Start updating the timestamp every second
    setInterval(() => {
      this.currentTime = new Date().toLocaleString();
    }, 1000);
  }

  ngOnInit(): void {
    this.themeService.setTheme(this.selectedTheme);
    this.primengConfig.ripple = true;

  }

  onThemeChange(theme: string): void {
    this.selectedTheme = theme;
    this.themeService.setTheme(theme);
  }
}
