import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class IframeService {
  private iframeSrc = new BehaviorSubject<string>('http://127.0.0.1:8050/');
  currentSrc = this.iframeSrc.asObservable();

  updateSrc(port: number) {
    this.iframeSrc.next(`http://127.0.0.1:${port}/`);
  }
}
