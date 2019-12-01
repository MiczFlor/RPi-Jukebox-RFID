<center>
    <img id="cover" class='img-responsive img-thumbnail' src='api/cover.php' alt='Cover'/>
</center>

<script>
    function loadCover() {
        $("#cover").attr('src', 'api/cover.php?t=' + new Date().getTime());
    }
    $(document).ready(() => {
        JUKEBOX.playlistChangedListener.push(loadCover);
    });
</script>
