// Debug script to test authentication flow
console.log("=== Debugging Authentication Flow ===");

// Test 1: Check localStorage before login
console.log("1. localStorage before login:");
console.log("   token:", localStorage.getItem("token"));
console.log("   refresh_token:", localStorage.getItem("refresh_token"));
console.log("   token_expiry:", localStorage.getItem("token_expiry"));

// Test 2: Simulate login
async function testLogin() {
    console.log("2. Testing login...");
    
    try {
        const response = await fetch("/api/v1/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: "admin",
                password: "admin123"
            })
        });
        
        console.log("   Login response status:", response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log("   Login successful, got token:", data.access_token ? "YES" : "NO");
            
            // Test 3: Check localStorage after login
            console.log("3. localStorage after login:");
            console.log("   token:", localStorage.getItem("token"));
            console.log("   refresh_token:", localStorage.getItem("refresh_token"));
            console.log("   token_expiry:", localStorage.getItem("token_expiry"));
            
            // Test 4: Test /auth/me with token
            console.log("4. Testing /auth/me...");
            const token = localStorage.getItem("token");
            console.log("   Using token:", token ? "YES" : "NO");
            
            if (token) {
                const profileResponse = await fetch("/api/v1/auth/me", {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                });
                
                console.log("   Profile response status:", profileResponse.status);
                if (profileResponse.ok) {
                    const profileData = await profileResponse.json();
                    console.log("   Profile data:", profileData);
                } else {
                    console.log("   Profile error:", await profileResponse.text());
                }
            }
        } else {
            console.log("   Login failed:", await response.text());
        }
    } catch (error) {
        console.error("   Login error:", error);
    }
}

// Run the test
testLogin(); 