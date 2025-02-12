import { Component } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { IframeService } from '../services/iframe.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    ButtonModule
  ],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css'
})
export class SidebarComponent {
  constructor(private iframeService: IframeService) {}

  changePort(port: number) {
    this.iframeService.updateSrc(port);
  }
}
