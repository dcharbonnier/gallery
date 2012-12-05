define([
// Application.
"app", "plugins/spin",

],

// Map dependencies from above array.

function(app, Spinner) {

  var Views = {};


  Views.Header = Backbone.View.extend({
    template: 'medias/header',

    _breadcrumbs: null,

    initialize: function(options) {
      this._breadcrumbs = options.breadcrumbs;
      this._breadcrumbs.bind('reset', this.render, this);
    },

    render: function(template, context) {
      var context = context || {};
      context = _.extend({}, context, {
        breadcrumbs: this._breadcrumbs
      });
      return template(context);
    }

  });

  Views.Selection = Backbone.View.extend({
    template: 'medias/selection',

    events : {
      "click .select-all" : "selectAll",
      "click .unselect-all" : "unSelectAll",
      "click .revert-selection" : "revertSelection"
    },

    selectAll : function (event) {
      event.preventDefault();
      event.stopImmediatePropagation();

      app.paginator.page.each(function (o,id, col) {
        var silent = id < col.length - 1;
        o.set({'selected' : true}, {silent : silent});
      })
    },

    unSelectAll : function (event) {
      event.preventDefault();
      event.stopImmediatePropagation();

      app.paginator.page.each(function (o,id, col) {
        var silent = id < col.length - 1;
        o.set({'selected' : false}, {silent : silent});
      })
    },

    revertSelection : function (event) {
      event.preventDefault();
      event.stopImmediatePropagation();

      app.paginator.page.each(function (o,id, col) {
        var silent = id < col.length - 1;
        o.set({'selected' : !o.get('selected')}, {silent : silent});
      })
    },

    initialize : function () {
      this.collection.bind('all', this.render, this);

    },

    render: function (template, context) {

      context = {hasSelected : this.collection.length > 0}
      context.hasDeleted = this.collection.where({status : 'deleted'}).length > 0;
      context.hasPublished = this.collection.where({status : 'published'}).length > 0

      return template(context);
    }

  })

  Views.SideBar = Backbone.View.extend({
    template: 'medias/sidebar',

    _facetting: null,
    _selectionView : null,
    initialize: function(options) {
      this._facetting = options.facetting;

      // reset
      this.paginator = app.paginator;
      this.paginator.bind('change:current', this._resetSelectionView, this);
    },

    render: function(template, context) {
      var context = context || {};
      context = _.extend({}, context, {
        facetting: this._facetting
      });
      return template(context);
    },

    afterRender: function() {
      this._resetSelectionView();
    },

    _resetSelectionView: function() {
      // if there is no album display currently
      if (app.page.value === null) {
        return;
      }

      if (this._selectionView !== null) {
        this._selectionView.remove();
        this._selectionView = null;

        app.paginator.page.each(function (o, id, col) {
          o.set({'selected': false}, {silent : id < col.length -1 });
        });
      }



      var selectionView = new Views.Selection({
        collection: this.paginator.page.createLiveChildCollection().setPill('selected', {
          prefixes: ['selected:'],
          callback: function(model, value) {
            return model.get('selected') == true;
          }
        }).setSearchString('selected:true').query()
      });
      this._selectionView  = selectionView;
      this.$el.append(selectionView.$el);
      selectionView.render();
    }
  });

  var ImageOps = {

    mask: null,

    rotate: function(event) {

      event.preventDefault();
      event.stopImmediatePropagation();

      this._applyMask();

      var value = $(event.currentTarget).attr('data-rotate') || $(event.originalEvent.srcElement).attr('data-rotate');

      this.model.rotate(value, _.bind(function(response) {
        var $img = this.$el.find('.thumbnail-container img');
        $img.fadeOut(200, _.bind(function() {
          $img.attr('src', response.thumbnails[this.thumb_size].url + '?' + Math.random());
          $img.attr('width', response.thumbnails[this.thumb_size].width);
          $img.attr('height', response.thumbnails[this.thumb_size].height);
          $img.fadeIn(200);
          this._removeMask();

          this.model.set(response, {
            silent: true
          });

        }, this));

      }, this));
    },

    _applyStatus: function(status, callback) {
      this.model.set('status', status);
      this.model.save().then(callback);
    },

    mRemove: function(event) {
      event.preventDefault();
      event.stopImmediatePropagation();

      this._applyMask();
      this._applyStatus('deleted', _.bind(this._removeMask, this));
    },

    restore: function(event) {
      event.preventDefault();
      event.stopImmediatePropagation();
      this._applyMask();
      this._applyStatus('published', _.bind(this._removeMask, this));
    },

    toggleSelect: function(event) {
      event.preventDefault();
      event.stopImmediatePropagation();
      this.model.set('selected', !this.model.get('selected'));
    },


    _applyMask: function() {
      if(this.mask !== null) {
        return false;
      }
      var $thumb = this.$el.find('.thumb-container');
      var offset = $thumb.offset();

      var width = $thumb.width() + parseInt($thumb.css('padding')) * 2 + parseInt($thumb.css('border-width')) * 2;
      var height = $thumb.height() + parseInt($thumb.css('padding')) * 2 + parseInt($thumb.css('border-width')) * 2;
      var $mask = $('<div id="mask-' + this.model.cid + '" class="image-mask" style="display:none"></div>')
      $('body').append($mask);
      $mask.css({
        top: offset.top + 'px',
        left: offset.left + 'px',
        height: height + 'px',
        width: width + 'px'
      })

      $mask.fadeIn(50, _.bind(function() {
        this.mask = this._createSpin($mask.attr('id'));
      }, this));
      $thumb.find('.actions').fadeOut(50);

      return true;
    },

    _removeMask: function() {
      var $mask = $("#mask-" + this.model.cid)
      $mask.fadeOut(200, _.bind(function() {
        this.mask.stop();
        $mask.remove();
        this.mask = null;
      }, this));
    },

    _createSpin: function(targetId) {
      var opts = {
        lines: 17,
        // The number of lines to draw
        length: 11,
        // The length of each line
        width: 4,
        // The line thickness
        radius: 13,
        // The radius of the inner circle
        corners: 1,
        // Corner roundness (0..1)
        rotate: 0,
        // The rotation offset
        color: '#DDD',
        // #rgb or #rrggbb
        speed: 1,
        // Rounds per second
        trail: 100,
        // Afterglow percentage
        shadow: false,
        // Whether to render a shadow
        hwaccel: false,
        // Whether to use hardware acceleration
        className: 'spinner',
        // The CSS class to assign to the spinner
        zIndex: 2e9,
        // The z-index (defaults to 2000000000),
        top: 'auto',
        left: 'auto'
      };

      var target = document.getElementById(targetId);
      return new Spinner(opts).spin(target);
    }
  };

  Views.Detail = Backbone.View.extend(_.extend({
    template: 'medias/detail',

    thumb_size: 'medium',

    events: {
      "click .remove": "mRemove",
      "click .restore": "restore",
      "click .rotate": "rotate"
    },

    initialize: function() {
      this.model.bind('all', this.render, this);
    },

    serialize: function() {
      return {
        object: this.model.toJSON()
      };
    },


  }, ImageOps));

  Views.Item = Backbone.View.extend(_.extend({

    tagName: "li",
    className: "span2",

    thumb_size: 'small',

    events: {
      "mouseover": "show",
      "mouseout": "hide",
      "click .remove": "mRemove",
      "click .restore": "restore",
      "click .rotate": "rotate",
      "click .select": "toggleSelect",
    },

    serialize: function() {
      return {
        object: this.model.toJSON()
      };
    },

    displayImageActions: null,



    show: function() {
      if(this.model.get('is_an_album') == 1 || this.mask !== null) {
        return;
      }
      this.$el.find('.actions').slideDown(200);

      if(this.displayImageActions !== null) {
        clearTimeout(this.displayImageActions);
        this.displayImageActions = null;
      }
    },

    hide: function() {

      if(this.model.get('is_an_album') == 1) {
        return;
      }

      if(this.displayImageActions !== null) {
        clearTimeout(this.displayImageActions);
        this.displayImageActions = null;
      }

      this.displayImageActions = setTimeout(_.bind(function() {
        this.$el.find('.actions').fadeOut(200);
      }, this), 400)
    }
  }, ImageOps));



  Views.Items = Backbone.View.extend({

    initialize: function() {
      this.collection.bind('all', this.render, this);
    },

    tagName: "ul",
    className: "thumbnails",


    beforeRender: function() {
      this.collection.each(_.bind(function(model, pos) {
        if(model.get('is_an_album') === 1) {
          view = new Views.Item({
            model: model,
            template: 'medias/list/item-album'
          });

        } else {
          view = new Views.Item({
            model: model,
            template: 'medias/list/item-default'

          });

        }
        this.insertView(view);
      }, this));


    }
  });

  return Views;

});