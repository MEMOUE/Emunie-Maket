import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ActivatePremium } from './activate-premium';

describe('ActivatePremium', () => {
  let component: ActivatePremium;
  let fixture: ComponentFixture<ActivatePremium>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ActivatePremium]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ActivatePremium);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
