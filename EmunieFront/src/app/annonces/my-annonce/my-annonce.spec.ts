import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyAnnonce } from './my-annonce';

describe('MyAnnonce', () => {
  let component: MyAnnonce;
  let fixture: ComponentFixture<MyAnnonce>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MyAnnonce]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MyAnnonce);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
