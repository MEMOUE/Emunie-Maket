import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PaymentMethodDialog } from './payment-method-dialog';

describe('PaymentMethodDialog', () => {
  let component: PaymentMethodDialog;
  let fixture: ComponentFixture<PaymentMethodDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PaymentMethodDialog]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PaymentMethodDialog);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
