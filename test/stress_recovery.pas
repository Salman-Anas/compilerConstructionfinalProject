program stressTest ;
begin
    { Error 1: Missing expression after assignment }
    brokenVar := ;
    
    safeVar := 10 ;
    
    { Error 2: Unmatched parenthesis and missing operator }
    brokenMath := ( safeVar + 5  safeVar ;
    
    { Error 3: Invalid token sequence }
    badTokens := 10 + * 20 ;
    
    { Valid statement at the end to prove the compiler survived }
    survivalCheck := safeVar * 2
end .