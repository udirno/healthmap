# Test Plan - Music Explorer Map

## Manual Testing Checklist

### 1. Basic App Launch
- [ ] App starts without errors
- [ ] All tabs load (Explore, Tech README, Data Guide)
- [ ] Map displays with default data
- [ ] No console errors

### 2. Data Loading
- [ ] Default synthetic data loads
- [ ] iTunes generator creates dataset
- [ ] CSV upload works
- [ ] "Use this dataset in the app now" updates the map
- [ ] Session state persists across tab switches

### 3. Explore Tab Functionality
- [ ] Sliders affect the displayed tracks
- [ ] Genre filter works
- [ ] Track selection shows recommendations
- [ ] Hover shows track details
- [ ] Genre legend displays correctly

### 4. Data Guide Tab
- [ ] iTunes search generates results
- [ ] CSV upload validates schema
- [ ] Download buttons work
- [ ] "Use now" buttons update session state

### 5. Recommendations
- [ ] Similar tracks display without errors
- [ ] Similarity scores are reasonable
- [ ] No numpy errors in console

### 6. Visual Elements
- [ ] Colors are distinct for different genres
- [ ] Charts are readable and informative
- [ ] Layout is responsive
- [ ] Hover effects work

## Test Data Scenarios

### Scenario 1: Fresh Start
1. Clear browser cache
2. Launch app
3. Verify default data loads
4. Test basic interactions

### Scenario 2: iTunes Data Flow
1. Go to Data Guide
2. Search for "jazz classics"
3. Generate dataset
4. Use in app
5. Switch to Explore
6. Verify new data appears

### Scenario 3: CSV Upload Flow
1. Prepare test CSV with 10 tracks
2. Upload via Data Guide
3. Use in app
4. Verify data appears correctly

### Scenario 4: Mixed Genres
1. Generate data with diverse genres
2. Verify all genres get distinct colors
3. Test genre filtering
4. Check recommendations work

## Error Scenarios

### Invalid CSV
- [ ] Wrong column names
- [ ] Missing required columns
- [ ] Invalid data types
- [ ] Empty file

### Network Issues
- [ ] iTunes API timeout
- [ ] Slow responses
- [ ] Connection errors

### Data Edge Cases
- [ ] Single track dataset
- [ ] All tracks same genre
- [ ] Extreme coordinate values
- [ ] Missing track names

## Performance Testing
- [ ] 50 tracks: < 2s load
- [ ] 200 tracks: < 5s load
- [ ] 500 tracks: < 10s load
- [ ] Slider interactions: < 1s response

## Browser Compatibility
- [ ] Chrome (latest)
- [ ] Safari (latest)
- [ ] Firefox (latest)
- [ ] Mobile responsive

## Known Issues to Test
1. **Critical**: numpy sqrt error in recommendations
2. **UX**: Manual tab switch after "Use now"
3. **Visual**: New genres color mapping
4. **Performance**: Large dataset handling

## Test Results Template
```
Date: ___________
Tester: ___________
Version: ___________

Basic Launch: [ ] Pass [ ] Fail
Data Loading: [ ] Pass [ ] Fail
Explore Tab: [ ] Pass [ ] Fail
Data Guide: [ ] Pass [ ] Fail
Recommendations: [ ] Pass [ ] Fail
Visual Elements: [ ] Pass [ ] Fail

Issues Found:
1. ________________
2. ________________
3. ________________

Overall Status: [ ] Ready [ ] Needs Fixes
```

## Automated Testing (Future)
- Unit tests for core functions
- Integration tests for data flow
- Visual regression tests
- Performance benchmarks
