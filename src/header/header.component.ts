import { Component } from '@angular/core';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { Router } from '@angular/router';
import { ImageModule } from 'primeng/image';
import { InputSwitchModule } from 'primeng/inputswitch';
import { FormsModule } from '@angular/forms';


@Component({
  selector: 'app-header',
  standalone: true,
  imports: [
    CardModule,
    ButtonModule,
    ImageModule,
    InputSwitchModule,
    FormsModule
  ],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css'
})
export class HeaderComponent {
  currentTime: string;
  checked: boolean = false;


  constructor(
    private router: Router,
  ) {
    this.currentTime = new Date().toLocaleString();

    // Start updating the timestamp every second
    setInterval(() => {
      this.currentTime = new Date().toLocaleString();
    }, 1000);
  }

  ngOnInit() {

  }


}
