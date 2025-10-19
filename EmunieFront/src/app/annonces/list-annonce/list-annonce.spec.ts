import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListAnnonce } from './list-annonce';

describe('ListAnnonce', () => {
  let component: ListAnnonce;
  let fixture: ComponentFixture<ListAnnonce>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListAnnonce]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListAnnonce);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
