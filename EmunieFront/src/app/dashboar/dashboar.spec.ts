import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Dashboar } from './dashboar';

describe('Dashboar', () => {
  let component: Dashboar;
  let fixture: ComponentFixture<Dashboar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Dashboar]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Dashboar);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
