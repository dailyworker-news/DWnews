/**
 * Test Fixtures for Articles
 */

export const mockArticles = [
  {
    id: 1,
    title: "Workers Win Major Victory in Amazon Union Drive",
    slug: "workers-win-amazon-union",
    summary: "Amazon workers in Staten Island successfully unionize in historic vote.",
    category_name: "Labor & Unions",
    is_national: true,
    is_local: false,
    is_ongoing: true,
    is_new: false,
    status: "published",
    published_at: "2024-01-01T10:00:00Z",
    created_at: "2023-12-30T08:00:00Z"
  },
  {
    id: 2,
    title: "Healthcare Workers Demand Better Protections",
    slug: "healthcare-workers-protections",
    summary: "Healthcare workers organize for better workplace safety.",
    category_name: "Labor & Unions",
    is_national: false,
    is_local: true,
    is_ongoing: true,
    is_new: true,
    status: "published",
    published_at: "2024-01-02T12:00:00Z",
    created_at: "2024-01-02T10:00:00Z"
  },
  {
    id: 3,
    title: "New Study Shows Wage Theft Costs Workers Billions",
    slug: "wage-theft-study-billions",
    summary: "New research quantifies massive scale of wage theft in America.",
    category_name: "Labor & Unions",
    is_national: true,
    is_local: false,
    is_ongoing: false,
    is_new: true,
    status: "published",
    published_at: "2024-01-03T14:00:00Z",
    created_at: "2024-01-03T12:00:00Z"
  }
];

export const mockArticleDetail = {
  id: 1,
  title: "Workers Win Major Victory in Amazon Union Drive",
  slug: "workers-win-amazon-union",
  body: "In a historic victory, Amazon warehouse workers in Staten Island voted to form the company's first union...",
  summary: "Amazon workers in Staten Island successfully unionize in historic vote.",
  category_name: "Labor & Unions",
  category_slug: "labor-unions",
  author: "The Daily Worker Editorial Team",
  is_national: true,
  is_local: false,
  region_name: "National",
  is_ongoing: true,
  is_new: false,
  reading_level: 8.2,
  word_count: 1200,
  image_url: "https://example.com/amazon-union.jpg",
  image_attribution: "Photo by Worker Solidarity News",
  why_this_matters: "This represents a major breakthrough in organizing tech sector workers.",
  what_you_can_do: "Support union organizing efforts in your workplace.",
  status: "published",
  published_at: "2024-01-01T10:00:00Z",
  created_at: "2023-12-30T08:00:00Z"
};
