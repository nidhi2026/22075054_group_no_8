$(document).ready(function() {
    const searchUrl = $('#search').closest('form').data('search-url');

    $('#search').on('input', function() {
        // Clear the previous results
        $('#results').empty();
        $('#old-results').empty();

        $.ajax({
            url: searchUrl,
            data: {
                'q': $(this).val(),
            },
            dataType: 'json',
        }).done(function(data) {
            // Parse the response data
            const results = data;
            // Loop through each result
            results.forEach(item => {

                // printing the fetched data into console
                 console.log(JSON.stringify(item));

                if (item.title !== "No anime available with this name") {
                    // Use template literals to create HTML elements
                    const cardDiv = $(`
                        <div class="card h-100">
                            <a href="/anime/${item.id}">
                                <p class="title">${item.title}</p>
                                <img src="${item.image_url}" alt="${item.title}" class="card-img-top" style="object-fit: cover;top:0;">
                            </a>
                        </div>
                    `);
                    const resultDiv = $('<div>').addClass('col-lg-2 col-md-3 col-sm-4 mb-4').append(cardDiv);
                    $('#results').append(resultDiv);
                } else {
                    $('#results').append('<p>Nothing more to display...</p>');
                }
            });
        }).fail(function(error) {
            // Handle the error response
            console.log(error);
            $('#results').append('<p>Something went wrong...</p>');
        });
    });
});


// $(document).ready(function() {
//     const searchUrl = $('#search').closest('form').data('search-url');

//     $('#search').on('input', function() {
//         // Clear the previous results
//         $('#results').empty();

//         $.ajax({
//             url: searchUrl,
//             data: {
//                 'q': $(this).val(),
//             },
//             dataType: 'json',
//             success: function(data) {
//                 const results = $('#results');
//                 results.empty();
//                 data.forEach(item => {
//                     if (item.title !== "No anime available with this name") {
//                         const cardDiv = $('<div>').addClass('card h-100');
//                         const image = $('<img>').attr('src', item.image_url).attr('alt', item.title).addClass('card-img-top').css('object-fit', 'cover');
//                         const title = $('<p>').text(item.title).addClass('title');
//                         const link = $('<a>').attr('href', '/anime/' + item.id).append(image, title);

//                         cardDiv.append(link);

//                         const resultDiv = $('<div>').addClass('col-lg-2 col-md-3 col-sm-4 mb-4').append(cardDiv);
//                         results.append(resultDiv);
//                     } else {
//                         results.append('<p>Nothing more to display...</p>');
//                     }
//                 });
//             }
//         });
//     });
// });
