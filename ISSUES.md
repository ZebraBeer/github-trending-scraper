# Issues and Feature Requests

## Issues

1. **Improve error handling in trending history route**
   - In the `/trending/history` route, there is a try-except block for date parsing but it doesn't provide any feedback to the user if an invalid date format is provided.
   - Add error handling for cases where no repositories are found.

2. **Performance optimization for large datasets**
   - The history page might become slow as the number of records in the database grows, especially when loading all dates for the dropdown filter.
   - Implement pagination or lazy-loading for large datasets.

3. **UI enhancements for date selection**
   - Replace the simple dropdown with a more user-friendly date picker widget.
   - Add loading indicators when filtering by date to improve user experience.

4. **Add automated tests**
   - There appear to be no automated tests for the application, which could lead to regressions in the future.
   - Consider adding unit tests and integration tests.

5. **Address SQLAlchemy deprecation warnings**
   - There are some SQLAlchemy 2.0 deprecation warnings that should be addressed:
     ```
     MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base().
     ```

## Feature Requests

1. **Side-by-side comparison of trends**
   - Allow users to compare trends between different dates side by side.

2. **Advanced filtering options**
   - Add more filtering options in the history page (e.g., by stars, forks, or specific time ranges).

3. **Search functionality in history page**
   - Implement search functionality in the history page similar to what's available on the main trending page.