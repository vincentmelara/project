import { ButtonModule } from 'primeng/button';
import { Component, OnInit } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { TabMenuModule } from 'primeng/tabmenu';
import { SplitterModule } from 'primeng/splitter';
import { CardModule } from 'primeng/card';
import { HeaderComponent } from "../header/header.component";
import { SidebarComponent } from "../sidebar/sidebar.component";
import { TabViewModule } from 'primeng/tabview';
import { SettingsPageComponent } from "../settings-page/settings-page.component";
import { HeatmapPageComponent } from "../heatmap/heatmap-page.component";
import { IframeService } from '../services/iframe.service';

import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    TabMenuModule,
    SplitterModule,
    CardModule,
    HeaderComponent,
    SidebarComponent,
    TabViewModule,
    SettingsPageComponent,
    HeatmapPageComponent,
    ButtonModule
],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent {
  menuItems: MenuItem[];
  iframeSrc: SafeResourceUrl;


  constructor(private iframeService: IframeService, private sanitizer: DomSanitizer) {
    // Define tabs for the top tab menu
    this.menuItems = [
      {
        label: 'Tab 1',
        icon: 'pi pi-fw pi-home',
        command: () => {
          // Handle Tab 1 click
        }
      },
      {
        label: 'Tab 2',
        icon: 'pi pi-fw pi-calendar',
        command: () => {
          // Handle Tab 2 click
        }
      },
      {
        label: 'Tab 3',
        icon: 'pi pi-fw pi-pencil',
        command: () => {
          // Handle Tab 3 click
        }
      }
    ];
    this.iframeSrc = this.sanitizer.bypassSecurityTrustResourceUrl('http://127.0.0.1:8050/');
  }
  ngOnInit() {
    this.iframeService.currentSrc.subscribe(src => {
      this.iframeSrc = this.sanitizer.bypassSecurityTrustResourceUrl(src);
    });
  }


  changePort(port: number) {
    this.iframeSrc = `http://127.0.0.1:${port}/`;
  }
}
