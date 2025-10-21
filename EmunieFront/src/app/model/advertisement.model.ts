export interface Advertisement {
  id?: number;
  title: string;
  link: string;
  image: string;
  start_date: string;
  end_date?: string;
  duration_hours: number;
  total_price?: number;
  price_per_day: number;
}
