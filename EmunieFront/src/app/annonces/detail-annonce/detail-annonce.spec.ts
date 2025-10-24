import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DetailAnnonce } from './detail-annonce';

describe('DetailAnnonce', () => {
  let component: DetailAnnonce;
  let fixture: ComponentFixture<DetailAnnonce>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DetailAnnonce]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DetailAnnonce);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
