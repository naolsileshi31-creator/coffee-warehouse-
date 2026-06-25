# 2. HTML Frontend
HTML_CODE = """
<!DOCTYPE html>
<html lang="am">
<head><title>የቡና መጋዘን ክምችት</title></head>
<body style="font-family: sans-serif; padding: 20px;">
    <h1>☕ የቡና መጋዘን ክምችት መቆጣጠሪያ</h1>
    <form action="/add" method="post">
        <input name="batch_number" placeholder="የባች ቁጥር" required><br><br>
        <input name="coffee_type" placeholder="የቡና አይነት" required><br><br>
        <input name="grade" placeholder="ደረጃ" required><br><br>
        <button type="submit">መዝግብ</button>
    </form>
    <h2>የተመዘገቡ ቡናዎች</h2>
    <a href="/stocks">ክምችቱን ይመልከቱ</a>
</body>
</html>
"""
