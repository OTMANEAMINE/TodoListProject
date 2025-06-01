(function($) {
    $(document).ready(function() {
        var userSelect = $('#id_user');
        var categorySelect = $('#id_category');
        
        function updateCategoryOptions() {
            var userId = userSelect.val();
            if (userId) {
                // Sauvegarder la catégorie actuellement sélectionnée
                var currentCategory = categorySelect.val();
                
                // Faire une requête AJAX pour obtenir les catégories de l'utilisateur
                $.getJSON('/admin/todos/task/categories/', {'user': userId}, function(data) {
                    // Vider et reconstruire la liste des catégories
                    categorySelect.empty();
                    categorySelect.append($('<option value="">---------</option>'));
                    
                    $.each(data, function(index, category) {
                        var option = $('<option></option>')
                            .val(category.id)
                            .text(category.name)
                            .css('background-color', category.color + '20');
                        categorySelect.append(option);
                    });
                    
                    // Restaurer la sélection si la catégorie existe toujours
                    if (currentCategory) {
                        categorySelect.val(currentCategory);
                    }
                });
            } else {
                // Si aucun utilisateur n'est sélectionné, vider la liste des catégories
                categorySelect.empty();
                categorySelect.append($('<option value="">---------</option>'));
            }
        }
        
        // Mettre à jour les catégories quand l'utilisateur change
        userSelect.change(updateCategoryOptions);
        
        // Mettre à jour les catégories au chargement de la page
        if (userSelect.val()) {
            updateCategoryOptions();
        }
    });
})(django.jQuery); 