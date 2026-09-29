# iOS project structure

```
ios/
  MoviesApp.xcodeproj
  MoviesApp/
    MoviesAppApp.swift
    App/                  # composition root, coordinator
    Features/
      Home/
      Search/
      Wishlist/
      Rating/
    Models/
    Services/
    DesignSystem/
    Resources/
  MoviesAppTests/
```

New Jira screens belong in `Features/<Name>/` as `*View.swift` + `*ViewModel.swift`.
