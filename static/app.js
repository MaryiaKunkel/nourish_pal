$(document).ready(function () {
    console.log('Script executed!');
    $('.like-button').click(function() {
        let button = $(this);
        let recipeId = button.data('recipe-id');
        
        $.ajax({
            type: 'POST',
            url: '/users/add_like/' + recipeId,
            success: function(data) {
                if (data.is_liked) {
                    button.html('<i class="fas fa-bookmark fa-2x" style="color: red;"></i>');
                } else {
                    button.html('<i class="far fa-bookmark fa-2x"></i>');
                }
            },
            error: function(error) {
                console.error('Error:', error);
            }
        });
    });
});