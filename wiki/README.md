# Schema Sentinel Wiki

This directory contains the wiki documentation for Schema Sentinel. The wiki provides comprehensive guides and documentation for users and contributors.

## Wiki Pages

- **[Home.md](Home.md)** - Welcome page and overview of the project
- **[Getting-Started.md](Getting-Started.md)** - Installation and quick start guide
- **[Architecture.md](Architecture.md)** - System architecture and design documentation
- **[Development.md](Development.md)** - Development environment setup and guidelines
- **[Contributing.md](Contributing.md)** - How to contribute to the project
- **[Security.md](Security.md)** - Security guidelines and best practices
- **[Future-Development-Plan.md](Future-Development-Plan.md)** - Roadmap and upcoming features

## Using the Wiki

### For Local Reference

These markdown files can be read directly in any markdown viewer or text editor. They are written to be readable both on GitHub and locally.

### Publishing to GitHub Wiki

To publish these pages to the GitHub wiki:

1. **Clone the wiki repository:**
   ```bash
   git clone https://github.com/Igladyshev/schema-sentinel.wiki.git
   ```

2. **Copy the wiki files:**
   ```bash
   cp wiki/*.md schema-sentinel.wiki/
   ```

3. **Commit and push:**
   ```bash
   cd schema-sentinel.wiki
   git add .
   git commit -m "Update wiki content"
   git push origin master
   ```

### Updating the Wiki

When updating wiki content:

1. Edit the markdown files in the `wiki/` directory
2. Test the rendering locally
3. Create a pull request with your changes
4. After merge, publish to GitHub wiki (if needed)

## Wiki Structure

Each wiki page is self-contained but cross-referenced with other pages. The structure follows a logical progression:

1. **Home** → Overview and navigation
2. **Getting Started** → First steps for new users
3. **Architecture** → Understanding the system
4. **Development** → For contributors
5. **Contributing** → Contribution process
6. **Security** → Security best practices
7. **Future Development Plan** → Roadmap and vision

## Maintenance

- Review and update wiki pages with each major release
- Ensure code examples are tested and working
- Keep links up-to-date
- Add new pages as needed for new features

## Contributing to Wiki

Contributions to the wiki are welcome! Please:

- Keep documentation clear and concise
- Use examples and code snippets
- Follow the existing style and format
- Test all code examples
- Update the table of contents when adding new sections

For more information, see [Contributing.md](Contributing.md).
