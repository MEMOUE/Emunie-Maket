import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewAnonce } from './new-anonce';

describe('NewAnonce', () => {
  let component: NewAnonce;
  let fixture: ComponentFixture<NewAnonce>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewAnonce]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NewAnonce);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
