import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewPublicite } from './new-publicite';

describe('NewPublicite', () => {
  let component: NewPublicite;
  let fixture: ComponentFixture<NewPublicite>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewPublicite]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NewPublicite);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
