import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Advertisement } from '../model/advertisement.model';

@Injectable({
  providedIn: 'root'
})
export class AdvertisementService {
  private baseUrl = 'http://localhost:8000/api/publicite/';

  constructor(private http: HttpClient) {}

  create(ad: FormData): Observable<Advertisement> {
    return this.http.post<Advertisement>(`${this.baseUrl}create/`, ad);
  }

  getAll(): Observable<Advertisement[]> {
    return this.http.get<Advertisement[]>(this.baseUrl);
  }

  getById(id: number): Observable<Advertisement> {
    return this.http.get<Advertisement>(`${this.baseUrl}${id}/`);
  }

  delete(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}${id}/`);
  }
}
