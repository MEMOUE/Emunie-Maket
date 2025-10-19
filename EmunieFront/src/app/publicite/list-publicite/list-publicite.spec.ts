import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListPublicite } from './list-publicite';

describe('ListPublicite', () => {
  let component: ListPublicite;
  let fixture: ComponentFixture<ListPublicite>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListPublicite]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListPublicite);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
