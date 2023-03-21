LANGUAGES = ['en', 'hu']

CONSTANTS = {
    "version" : "0.4.2 - Theresa",
    "years" : "2021-2023",
    "name" : "HBud",
    "main_url" : "https://github.com/swanux/hbud",
    "bug_url" : "https://github.com/swanux/hbud/issues/labels/bug",
    "help_url" : "https://github.com/swanux/hbud/issues",
    "app_id" : "io.github.swanux.hbud",

    "app_desc" : """Simple audio/video player and karaoke app written in Python and GTK4

Features:

    - Audio and video playback
    - Subtitle support
    - Karaoke mode (synced lyrics needed in own srt format, see GitHub for instructions)
    - Static lyric automatically from online sources
    - Metadata editor (for audio files)
    - Playlists (from folder structure)
    - Seamlessly switch between video and audio playback (remembers position)
    - Native, lightweight and simple
    - Minimalistic design
    - Customizable
    - Flatpak package for compatibility and security
""",

    "rel_notes" : """<p></p>
<ul>
    <li>Loading animation during playlist processing</li>
    <li>Added MPRIS integration</li>
    <li>Added ability to open multiple files at once from file browser</li>
    <li>Now possible to drag and drop files to open (video / audio / subtitle - detected automatically)</li>
    <li>Added keyboard shortcuts window + new shortcuts</li>
    <li>Reworked fullscreen video experience</li>
    <li>Added option to set fullscreen player UI opacity</li>
    <li>New right click menu option to play a track next</li>
    <li>Added option to clear cache</li>
    <li>New utility pane for managing multiple saved playlists (folder-based for now)</li>
    <li>Hardened flatpak permissions (no filesystem access at all!)</li>
    <li>Added animations to make changes in the UI more visually appealing / coherent</li>
    <li>Faster loading speed with artwork caching (noticable with larger playlists)</li>
    <li>Reduced flatpak installed size by around 50% (runtimes not included)</li>
    <li>Reworked and improved seeking and slider</li>
    <li>Changed the default icon for tracks without artwork</li>
    <li>Polished karaoke lyric display</li>
    <li>Lots of backend and frontend related fixes and improvements</li>
    <li>Restructured development environment and codebase</li>
    <li>Other minor UI and UX tweaks</li>
</ul>"""
}